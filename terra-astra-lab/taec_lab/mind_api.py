"""Mind API v2: stdlib HTTP surface over the TAEC Mind (read-only over banks).

v2 additions (server-capability upgrade, 2026-09-25):
  /health  -> liveness: uptime, pid, python, psutil mem/cpu (when available)
  /metrics -> persisted request counters per endpoint (SQLite at
              telemetry/mind-api.db), avg latency, uptime
  SQLite   -> every GET is recorded; the DB survives API restarts, so the
              counters are cumulative across restarts within the sandbox.

Unchanged: / (RTL dashboard), /status, /forecast, /lessons, /ledger.
Honesty: the API never writes mind banks or ledger state; its only writes
are its OWN metrics database. Forecasts remain advisory reads.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Vendored dependencies (phase 10): server/vendor is committed to the repo,
# so psutil survives sandbox revival WITHOUT any network or reinstall —
# the session-scoped-packages limitation does not apply to repo files.
_VENDOR = Path(__file__).resolve().parents[2] / "server" / "vendor"
if _VENDOR.is_dir():
    sys.path.insert(0, str(_VENDOR))

from .knowledge import KnowledgeBank
from .mind import TAECMind
from .realtrace import (
    DEFAULT_LEDGER,
    OPS_BRAIN_PATH,
    OpsPhaseBrain,
    forecast_next_ops,
    load_ledger,
)

try:  # optional capability (installed by server/boot.sh install)
    import psutil
except Exception:  # pragma: no cover - fine without it
    psutil = None

STARTED_AT = time.time()
DB_PATH = os.environ.get(
    "MIND_API_DB",
    str(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "telemetry", "mind-api.db")),
)

PAGE = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>TAEC Mind — Live</title>
<style>
 body {{ font-family: system-ui, 'Segoe UI', Tahoma, sans-serif; background:#0d1b1e; color:#e8f1f2; margin:0; padding:2rem; }}
 h1 {{ color:#7fd1c0; font-size:1.5rem; margin:0 0 .3rem; }}
 .sub {{ color:#9db4b8; font-size:.85rem; margin-bottom:1.5rem; }}
 .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem; }}
 .card {{ background:#12292e; border:1px solid #1f444c; border-radius:12px; padding:1rem 1.2rem; }}
 .card h2 {{ font-size:1rem; color:#e0b25c; margin:.1rem 0 .8rem; }}
 .big {{ font-size:1.9rem; font-weight:700; color:#7fd1c0; }}
 table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
 td {{ padding:.22rem .3rem; border-bottom:1px solid #1f444c; }}
 .bar {{ background:#1f444c; border-radius:4px; height:10px; position:relative; overflow:hidden; }}
 .muted {{ color:#9db4b8; }}
 code {{ color:#e0b25c; }}
</style></head><body>
<h1>🧠 TAEC Mind — لوحة حية (v2) <span id="live-badge" class="muted" style="font-size:.8rem">● live</span></h1>
<div class="sub">عقل خارجي فوق مساحة العمل — قراءة فقط • تحديث كل 30 ثانية • {generated_at} • uptime {uptime_min} د</div>
<div class="grid">
  <div class="card"><h2>الحالة (الاصطناعي)</h2>
    <div class="big">{mind_status}</div>
    <table>
      <tr><td>درس في البنك</td><td><b>{lessons}</b></td></tr>
      <tr><td>تحديثات الأوزان</td><td>{weights_updates}</td></tr>
      <tr><td>آثار تدريب</td><td>{train_traces}</td></tr>
    </table></div>
  <div class="card"><h2>الدماغ التشغيلية (الحقيقي)</h2>
    <div class="big"><span id="ops-transitions">{ops_transitions}</span> <span class="muted" style="font-size:.9rem">انتقال</span></div>
    <table>
      <tr><td>أنماط (طور|نوع)</td><td><b>{ops_pair_keys}</b></td></tr>
      <tr><td>تحديثات</td><td>{ops_updates}</td></tr>
      <tr><td>آخر صف مُتعلَّم</td><td>seq {ops_last_seq}</td></tr>
    </table></div>
  <div class="card"><h2>تنبؤ الخطوة الحقيقية التالية <span class="muted" style="font-size:.75rem">(استشاري)</span></h2>
    <table>{forecast_rows}</table>
    <div class="muted" style="margin-top:.6rem">بعد: <code>{last_verb}</code> في طور <code>{last_phase}</code></div></div>
  <div class="card"><h2>سجل الشغل الحقيقي</h2>
    <div class="big">{ledger_n} <span class="muted" style="font-size:.9rem">حدث</span></div>
    <table>{ledger_rows}</table></div>
  <div class="card"><h2>حياة السيرفر (v2)</h2>
    <div class="big"><span id="req-total">{requests_total}</span> <span class="muted" style="font-size:.9rem">طلب مخدوم</span></div>
    <table>
      <tr><td>الذاكرة المستخدمة</td><td><b>{mem_percent}%</b></td></tr>
      <tr><td>CPU الآن</td><td><b>{cpu_percent}%</b></td></tr>
      <tr><td>avg latency</td><td>{avg_ms} ms</td></tr>
    </table></div>
</div>
<div class="sub" style="margin-top:1.5rem">JSON: <code>/status</code> · <code>/forecast</code> · <code>/lessons</code> · <code>/ledger</code> · <code>/health</code> · <code>/metrics</code> · <code>/events</code> (SSE) — التنبؤات قراءات استشارية وليست تعليمات.</div>
<script src="/live.js"></script>
</body></html>"""


LIVE_JS = """// TAEC Mind live updates via SSE (no page refresh needed)
const badge = document.getElementById('live-badge');
if (badge && window.EventSource) {
  const source = new EventSource('/events');
  source.addEventListener('snapshot', (event) => {
    try {
      const data = JSON.parse(event.data);
      badge.textContent = 'live (SSE)';
      badge.style.color = '#7fd1c0';
      const ops = document.getElementById('ops-transitions');
      if (ops) ops.textContent = data.ops_transitions;
      const reqs = document.getElementById('req-total');
      if (reqs) reqs.textContent = data.requests_total;
    } catch (error) { /* ignore malformed frames */ }
  });
  source.onerror = () => {
    badge.textContent = 'reconnecting\u2026';
    badge.style.color = '#e0b25c';
  };
}
"""


def _json_bytes(payload) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")


def _db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS requests ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, endpoint TEXT, status INTEGER, dur_ms REAL)"
    )
    return connection


def _record(endpoint: str, status: int, dur_ms: float) -> None:
    try:
        connection = _db()
        connection.execute(
            "INSERT INTO requests (ts, endpoint, status, dur_ms) VALUES (?, ?, ?, ?)",
            (time.time(), endpoint, status, round(dur_ms, 3)),
        )
        connection.commit()
        connection.close()
    except Exception:
        pass  # metrics must never break serving


def _metrics() -> dict:
    connection = _db()
    total = connection.execute("SELECT COUNT(*), COALESCE(AVG(dur_ms),0) FROM requests").fetchone()
    per_endpoint = connection.execute(
        "SELECT endpoint, COUNT(*) FROM requests GROUP BY endpoint ORDER BY COUNT(*) DESC"
    ).fetchall()
    connection.close()
    return {
        "requests_total": total[0],
        "avg_latency_ms": round(total[1], 3),
        "per_endpoint": {name: count for name, count in per_endpoint},
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "db": DB_PATH,
    }


def _health() -> dict:
    payload = {
        "status": "ok",
        "version": 2,
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "pid": os.getpid(),
        "python": os.sys.version.split()[0],
    }
    if psutil is not None:
        payload["mem_percent"] = psutil.virtual_memory().percent
        payload["cpu_percent"] = psutil.cpu_percent(interval=None)
    return payload


def _collect() -> dict:
    mind = TAECMind()
    ops = OpsPhaseBrain.load(OPS_BRAIN_PATH)
    forecast = forecast_next_ops()
    try:
        ledger = load_ledger(DEFAULT_LEDGER)
    except FileNotFoundError:
        ledger = []
    return {"mind": mind, "ops": ops, "forecast": forecast, "ledger": ledger}


def _dashboard(data: dict) -> bytes:
    forecast = data["forecast"]
    candidates = forecast.get("candidates", [])[:5]
    top = max((c["probability"] for c in candidates), default=0.0) or 1.0
    width = int((candidates[0]["probability"] / top) * 100) if candidates else 0
    forecast_rows = "".join(
        f"<tr><td>{c['op']}</td>"
        f"<td style='width:45%'><div class='bar'><span style='width:{width}%'></span></div></td>"
        f"<td>{c['probability']:.3f}</td></tr>"
        for c in candidates
    )
    ledger_rows = "".join(
        f"<tr><td>#{row['seq']}</td><td><code>{row.get('verb')}</code></td>"
        f"<td class='muted'>{row.get('area')}</td><td>{row.get('phase')}</td></tr>"
        for row in reversed(data["ledger"][-8:])
    )
    metrics = _metrics()
    if psutil is not None:
        mem_percent, cpu_percent = psutil.virtual_memory().percent, psutil.cpu_percent(interval=None)
    else:
        mem_percent, cpu_percent = "-", "-"
    html = PAGE.format(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        uptime_min=int(metrics["uptime_seconds"] // 60),
        mind_status=data["mind"].status,
        lessons=len(data["mind"].bank),
        weights_updates=data["mind"].weights.meta.get("updates", 0),
        train_traces=data["mind"].weights.meta.get("train_traces", 0),
        ops_transitions=data["ops"].n_transitions,
        ops_pair_keys=len(data["ops"].pair_counts),
        ops_updates=data["ops"].meta.get("updates", 0),
        ops_last_seq=data["ops"].meta.get("last_seq_learned", 0),
        forecast_rows=forecast_rows,
        last_verb=forecast.get("base", {}).get("last_verb", "?"),
        last_phase=forecast.get("base", {}).get("phase", "?"),
        ledger_n=len(data["ledger"]),
        ledger_rows=ledger_rows,
        requests_total=metrics["requests_total"],
        avg_ms=metrics["avg_latency_ms"],
        mem_percent=mem_percent,
        cpu_percent=cpu_percent,
    )
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        started = time.perf_counter()
        path = self.path.split("?")[0]
        status = 200
        try:
            try:
                data = _collect()
            except FileNotFoundError:
                data = {"mind": TAECMind(), "ops": OpsPhaseBrain.load(OPS_BRAIN_PATH),
                        "forecast": {"candidates": [], "base": {}}, "ledger": []}
            if path == "/":
                self._send(_dashboard(data), "text/html; charset=utf-8")
            elif path == "/health":
                self._send(_json_bytes(_health()), "application/json; charset=utf-8")
            elif path == "/metrics":
                self._send(_json_bytes(_metrics()), "application/json; charset=utf-8")
            elif path == "/live.js":
                self._send(LIVE_JS.encode("utf-8"), "application/javascript; charset=utf-8")
            elif path == "/events":
                self._serve_events()
            elif path == "/status":
                mind, ops = data["mind"], data["ops"]
                self._send(_json_bytes({
                    "synthetic_mind": {
                        "status": mind.status, "lessons": len(mind.bank),
                        "weights_updates": mind.weights.meta.get("updates", 0),
                        "train_traces": mind.weights.meta.get("train_traces", 0),
                    },
                    "ops_brain": {
                        "path": str(OPS_BRAIN_PATH), "n_transitions": ops.n_transitions,
                        "pair_keys": len(ops.pair_counts), "meta": ops.meta,
                    },
                    "ledger": {"path": str(DEFAULT_LEDGER), "n_events": len(data["ledger"])},
                }), "application/json; charset=utf-8")
            elif path == "/forecast":
                self._send(_json_bytes(data["forecast"]), "application/json; charset=utf-8")
            elif path == "/lessons":
                items = sorted(data["mind"].bank.items.values(), key=lambda i: i.item_id)
                self._send(_json_bytes([
                    {"item_id": i.item_id, "title": i.title, "source": i.source,
                     "confidence": i.confidence, "use_count": i.use_count,
                     "success_count": i.success_count}
                    for i in items
                ]), "application/json; charset=utf-8")
            elif path == "/ledger":
                rows = data["ledger"][-30:]
                self._send(_json_bytes([
                    {k: row.get(k) for k in ("seq", "verb", "area", "phase", "detail",
                                             "outcome", "source")}
                    for row in reversed(rows)
                ]), "application/json; charset=utf-8")
            else:
                status = 404
                self.send_error(404)
        except Exception as error:  # surface errors as JSON, keep serving
            status = 500
            self._send(_json_bytes({"error": repr(error)}), "application/json; charset=utf-8")
        finally:
            if path != "/events":  # long-lived stream: keep latency metrics clean
                _record(path, status, (time.perf_counter() - started) * 1000)

    def _serve_events(self) -> None:
        """Server-Sent Events: push live snapshots every 2s (bounded to ~2min)."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            ops = OpsPhaseBrain.load(OPS_BRAIN_PATH)
            metrics = _metrics()
            snapshot = json.dumps({
                "ts": int(time.time()),
                "ops_transitions": ops.n_transitions,
                "requests_total": metrics["requests_total"],
            })
            self.wfile.write(f"event: snapshot\ndata: {snapshot}\n\n".encode("utf-8"))
            self.wfile.flush()
            for _ in range(60):  # ~2 minutes per connection, then client reconnects
                time.sleep(2)
                self.wfile.write(f": ping {int(time.time())}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass  # client disconnected; normal for SSE

    def log_message(self, *args) -> None:  # quiet
        return


def main() -> None:
    port = int(os.environ.get("MIND_API_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"TAEC Mind API v2 listening on 0.0.0.0:{port} (read-only; metrics={DB_PATH})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
