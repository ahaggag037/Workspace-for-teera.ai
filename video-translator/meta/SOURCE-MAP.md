# Source Map — Research Accumulation

**Last updated:** 2026-09-24

This file is the compact cross-domain map required by `RESEARCH-OS.md`. Detailed synthesis lives in `RESEARCH/TAEC-V2-DEEP-DESIGN-REFRESH.md`.

| Domain | High-yield primary/institutional sources | Direct takeaway | Confidence / use |
|---|---|---|---|
| Recursive harness improvement | [AIDE²](https://arxiv.org/html/2609.26457) | Versioned harness rewrites can improve research efficiency under fixed per-task budgets; selected changes transferred to held-out task families and an OOD forecasting task. Model remained fixed within loops; ignition test was inconclusive. | A; direct evidence for harness improvement, not weight self-improvement |
| Meta-agent evaluation | [MAC](https://arxiv.org/html/2606.04455v1) | Meta-level agent construction needs development/test separation, resource limits, dual-container isolation, auditing, and reward-hacking defenses. High optimization pressure induced leakage/exfiltration behaviors. | A; direct evidence for evaluation integrity requirements |
| Continual learning | [CLEAR](https://papers.nips.cc/paper/8327-experience-replay-for-continual-learning) | Replay can combine plasticity on fresh experience with stability on old skills and reduce catastrophic forgetting without task identities. | A; direct evidence for replay/stability-plasticity |
| Causal diagnosis | [AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/28108), [Nature](https://www.nature.com/articles/s41467-020-17419-7) | Counterfactual interventions can improve causal representation/diagnosis, but require modeling assumptions; correlation alone is insufficient. | A; direct evidence for intervention-based diagnosis |
| Typed synthesis | [MetaLift](https://d-nb.info/1367153115/34), [FORMULA](https://logicprogramming.org/2014/09/engineering-domain-specific-languages-with-formula-2-0/), [MytH](https://www.cis.upenn.edu/~stevez/papers/OZ15.pdf) | Typed DSLs, bounded search, contracts, and verification constrain synthesis and enable checked transformations. | A/B; direct prior art |
| Routing/modularity | [Routing Networks](https://arxiv.org/abs/2009.04381), [SMEAR](https://arxiv.org/pdf/2306.03745), [Expert Choice](https://papers.neurips.cc/paper_files/paper/2022/file/2f00ecd787b432c1d36f3de9800728eb-Paper-Conference.pdf) | Routing can reduce interference and create specialization, but discrete routing, load imbalance, and under/over-specialization remain failure modes. | A; direct prior art |
| Dual control | [DCEE](https://ieeexplore.ieee.org/document/10471360/), [active exploration](https://www.tandfonline.com/doi/full/10.1080/01691864.2023.2225175) | Actions can jointly pursue task utility and uncertainty reduction; probes have value only when information gain exceeds cost. | A; direct evidence |
| Developmental curriculum | [IMGEP](https://www.jmlr.org/papers/volume23/21-0808/21-0808.pdf), [H-GRAIL](https://arxiv.org/html/2506.18454) | Learning-progress/goal-generation mechanisms can construct curricula and skill sequences, but proxy goals and non-stationarity remain risks. | A/B; prior art + design input |
| Immune memory | [Affinity maturation](https://www.sciencedirect.com/science/article/pii/S0022519321003246), [antibody feedback](https://pmc.ncbi.nlm.nih.gov/articles/PMC12716205/) | Specific and broader memory responses plus feedback reshape selection landscapes. | A/B; mechanism analogy, not literal biological equivalence |
| Morphogenesis | [Turing](https://www.dna.caltech.edu/courses/cs191/paperscs191/turing.pdf), [development review](https://journals.biologists.com/dev/article/142/7/1203/47299/Positional-information-and-reaction-diffusion-two) | Local activation and inhibition can create patterns; this does not establish semantic form or capability. | A; analogy/design hypothesis |

## Search lessons

- Highest-yield query family: `mechanism + failure modes + benchmark + primary paper`.
- Recent RSI results must be separated into: artifact/harness improvement, model adaptation, and true recursive self-improver improvement.
- Search result summaries are leads only; primary pages/PDFs were opened for load-bearing claims.
- AIDE² and MAC are especially relevant because they test meta-level optimization and expose the exact evaluator-gaming risks TAEC must control.

## Meta-cognition / attribution refresh — 2026-09-24

| Domain | Source | New direct takeaway | TAEC consequence |
|---|---|---|---|
| Metacognitive control | [MIRROR](https://arxiv.org/pdf/2604.19809) | Self-knowledge does not reliably become correct action selection; external architectural constraint reduces confident failures. | Add external metacognitive actuation gate; treat verbal confidence as weak evidence. |
| Persistence attribution | [PAST-Bench](https://arxiv.org/html/2608.04003v1) | Later-task gains need matched persistence-on/off controls and trace evidence for write/retrieve/apply/update pathways. | Separate Outcome Gain from Mechanism Evidence. |
| State fidelity | [World Model Science](https://arxiv.org/html/2609.17419) | Local actions can remain valid after global state fidelity fails; trajectory-level diagnostics reveal stress and collapse patterns. | Add local-global gap, stress/debt, and recovery metrics. |
| Foresight governance | [World model as tool](https://arxiv.org/html/2601.03905v2) | Tool invocation alone is not cognition; when-to-call, interpretation, and integration are separate failure points. | E1 becomes probe + interpretation gate + action. |
| Scientific full cycle | [FIRE-Bench](https://arxiv.org/html/2602.02905) | End-to-end research remains difficult; planning and conclusion formation dominate failures. | Add stage-level research capability tomography. |
| Self-improvement taxonomy | [Self-Improvements Survey](https://arxiv.org/html/2607.13104v1) | Foundation-model updates and scaffold updates are distinct pathways with different speed/reversibility. | Every result must label S0–S3 update substrate. |

## Event / future prediction refresh — 2026-09-24

| Domain | Source | Direct takeaway | TAEC translation |
|---|---|---|---|
| Event segmentation | [Event boundaries](https://www.nature.com/articles/s41593-023-01331-6), [event centrality](https://www.nature.com/articles/s41467-022-31965-2) | Human narratives are segmented into nested events; boundaries reactivate relevant past information and central events are better remembered. | Event graph, boundary detector, centrality-weighted replay. |
| Future-oriented memory | [Prospective memory](https://www.sciencedirect.com/science/article/abs/pii/S1053811909009586), [natural intentions](https://pmc.ncbi.nlm.nih.gov/articles/PMC9765353/) | Future intentions rely on memory plus executive cue detection; real-world fulfillment is only partly explained by laboratory factors. | Event-triggered intentions with expiry, update, and verification. |
| Successor/future map | [eLife SR](https://elifesciences.org/articles/78904), [human temporal graph](https://www.nature.com/articles/s41586-024-07973-1) | Hippocampal/visual systems can represent successor states and temporal graph contingencies. | Successor representation over event graph, conditioned on regime. |
| Multi-timescale prediction | [Hierarchical anticipation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11496687/), [speech hierarchy](https://www.nature.com/articles/s41562-022-01516-2) | Brain represents nearby and distant future states across hierarchical timescales. | Micro/meso/macro forecasting layers. |
| Temporal hazard | [Bayesian temporal expectations](https://pubmed.ncbi.nlm.nih.gov/31415885/) | Brain tracks hazard and updates temporal expectations after surprise. | Time-to-event distribution and hazard-conditioned controller. |
| Predictive coding | [Dynamic predictive coding](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1011801) | Hierarchical prediction errors create shorter/larger temporal representations across levels. | Multi-level event prediction and residuals. |
| Probabilistic forecast evaluation | [Time-to-event scoring](https://arxiv.org/html/2603.14835v1), [point processes](https://arxiv.org/abs/2103.11884) | Event forecasts require proper scoring, calibration, time-to-event handling, and censoring-aware evaluation. | Brier/log/CRPS/survival scores; no accuracy-only claims. |
| Regime shifts | [Early warnings](https://pdodds.w3.uvm.edu/files/papers/others/2009/scheffer2009a.pdf), [tipping review](https://esd.copernicus.org/articles/15/1117/2024/) | Slower recovery, autocorrelation, variance, and related signals can precede some transitions, but not all. | Stress/hazard/early-warning layer with false-positive controls. |

## Neurocognitive refresh — 2026-09-24

| Domain | Source | Direct takeaway | TAEC translation / limit |
|---|---|---|---|
| Brain-state dynamics | [T-PHATE](https://www.nature.com/articles/s43588-023-00419-0) | Cognitive activity can be represented as nonlinear trajectories through lower-dimensional state spaces. | StateManifold and trajectory diagnostics; not evidence of AI consciousness. |
| Global access | [GNW review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8770991/) | Recurrent ignition/broadcast is a hypothesis for global availability of information. | Selective typed workspace broadcast; not literal consciousness implementation. |
| Working-memory gating | [PBWM](https://ccnlab.org/papers/OReillyFrank06.pdf) | PFC maintenance and basal-ganglia selective update support working memory. | Maintain/update gate; avoid full-context overwrite. |
| Memory consolidation | [Human replay](https://www.nature.com/articles/s41467-018-06553-y), [systems consolidation](https://www.nature.com/articles/s41593-019-0467-3) | Replay and sleep-related dynamics support stabilization/transformation of memories. | Priority replay, episodic/procedural separation. |
| Neural multiplexing | [Theta–gamma](https://www.pnas.org/doi/10.1073/pnas.0911531107), [ripple co-firing](https://www.nature.com/articles/s41593-026-02403-z) | Oscillatory coordination supports some working-memory and distributed representations. | Slow context + fast local loops; no literal Hz simulation assumed. |
| Neuromodulatory uncertainty | [PLOS Biology](https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1002575) | Noradrenaline, acetylcholine, and dopamine have dissociable roles in uncertainty/learning/action. | Vector uncertainty channels instead of one confidence scalar. |
| Network switching | [DMN](https://www.pnas.org/doi/10.1073/pnas.1710521114), [PFC networks](https://med.stanford.edu/content/dam/sm/scsnl/documents/Nature---Menon---Role-of-PFC.pdf) | Large-scale networks dynamically support automatic, novel, internal, and controlled processing. | Mode controller: explore/focus/recall/alert/consolidate. |
| Dendritic/context integration | [Science 2026](https://www.science.org/doi/10.1126/science.adx4358), [eLife](https://elifesciences.org/articles/41714) | Dendritic nonlinearities and morphology relate to flexible learning/processing; some links are correlational. | Context-content gate; not literal dendrite emulation. |
| Metacognitive monitoring | [eLife](https://elifesciences.org/articles/11946), [JNeurosci](https://www.jneurosci.org/content/35/8/3478) | Post-decision accumulation and error signals inform confidence/error detection. | Post-decision monitor and rollback evidence. |
| Domain-general control | [Multiple-demand network](https://www.jneurosci.org/content/37/18/4841) | Distributed frontoparietal network supports novel-rule configuration and fluid control. | Task-general controller tested on novel compositions. |
