"""Deterministic metrics for event and probabilistic forecasts."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Mapping, Sequence


def normalize(probabilities: Mapping[str, float], labels: Sequence[str]) -> dict[str, float]:
    values = {label: max(0.0, float(probabilities.get(label, 0.0))) for label in labels}
    total = sum(values.values())
    if total <= 0.0:
        uniform = 1.0 / len(labels) if labels else 0.0
        return {label: uniform for label in labels}
    return {label: value / total for label, value in values.items()}


def top_label(probabilities: Mapping[str, float]) -> str:
    """Order-independent argmax: ties break alphabetically.

    JSON round-trips can reorder keys (sort_keys=True), so naive max()
    tie-breaking would depend on serialization order. Found 2026-09-24.
    """
    return max(sorted(probabilities.items()), key=lambda item: item[1])[0]


def accuracy(y_true: Sequence[str], predictions: Sequence[Mapping[str, float]]) -> float:
    if not y_true:
        return 0.0
    return sum(top_label(prob) == truth for truth, prob in zip(y_true, predictions)) / len(y_true)


def multiclass_log_loss(
    y_true: Sequence[str], predictions: Sequence[Mapping[str, float]], labels: Sequence[str]
) -> float:
    if not y_true:
        return float("nan")
    losses = []
    for truth, probabilities in zip(y_true, predictions):
        normalized = normalize(probabilities, labels)
        losses.append(-math.log(max(normalized.get(truth, 0.0), 1e-12)))
    return sum(losses) / len(losses)


def brier_score(
    y_true: Sequence[str], predictions: Sequence[Mapping[str, float]], labels: Sequence[str]
) -> float:
    if not y_true:
        return float("nan")
    values = []
    for truth, probabilities in zip(y_true, predictions):
        normalized = normalize(probabilities, labels)
        values.append(sum((normalized[label] - (1.0 if label == truth else 0.0)) ** 2 for label in labels))
    return sum(values) / len(values)


def expected_calibration_error(
    y_true: Sequence[str], predictions: Sequence[Mapping[str, float]], bins: int = 10
) -> float:
    if not y_true:
        return float("nan")
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for truth, probabilities in zip(y_true, predictions):
        label = top_label(probabilities)
        confidence = probabilities[label]
        index = min(bins - 1, int(max(0.0, min(0.999999, confidence)) * bins))
        buckets[index].append((confidence, label == truth))
    total = len(y_true)
    error = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        mean_confidence = sum(item[0] for item in bucket) / len(bucket)
        mean_accuracy = sum(item[1] for item in bucket) / len(bucket)
        error += len(bucket) / total * abs(mean_confidence - mean_accuracy)
    return error


def boundary_f1(truth_boundaries: Iterable[int], predicted_boundaries: Iterable[int]) -> dict[str, float]:
    truth = set(truth_boundaries)
    predicted = set(predicted_boundaries)
    true_positive = len(truth & predicted)
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(truth) if truth else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def mean_absolute_error(values: Sequence[float]) -> float:
    return sum(abs(value) for value in values) / len(values) if values else float("nan")


def interval_coverage(actuals: Sequence[float], intervals: Sequence[tuple[float, float]]) -> float:
    if not actuals:
        return float("nan")
    covered = sum(low <= actual <= high for actual, (low, high) in zip(actuals, intervals))
    return covered / len(actuals)


def summarize_classification(
    y_true: Sequence[str], predictions: Sequence[Mapping[str, float]], labels: Sequence[str]
) -> dict[str, float]:
    return {
        "n": len(y_true),
        "accuracy": accuracy(y_true, predictions),
        "log_loss": multiclass_log_loss(y_true, predictions, labels),
        "brier": brier_score(y_true, predictions, labels),
        "ece": expected_calibration_error(y_true, predictions),
    }
