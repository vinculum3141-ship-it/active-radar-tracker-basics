# Trainer — Verification Rubrics

Grading guide for the milestone artifacts. The learner-facing checklist is
`docs/training/06-training.md` §7; this is the scoring version. Score each
artifact **P (pass) / P- (pass with note) / R (redo)** per criterion; a
P- on a criterion is acceptable once, R on any criterion → redo that
milestone.

Use the numbers below as the analytic truth (all from
`docs/training/01-physics.md` and the flowgraph constants).

## Milestone 1 — Range-Doppler map (Week 2)

Truth for the R=1000 m, v=40 m/s case: peak at range bin **~133**
(±1 bin), Doppler bin for the *aliased* velocity **−21.2 m/s**
(40 m/s > v_max = 30.6 m/s; ±Δv/2 = ±0.5 bin tolerance).

| Criterion | P | P- | R |
|---|---|---|---|
| Axes labeled range (m) and velocity (m/s) | both correct | one missing/unit error | neither |
| Peak within 1 range bin and Δv/2 | yes | off by 1 bin on one axis | off > 1 bin / missing |
| Aliasing handled honestly | peak annotated as aliased, or test explains it | note in code, no plot annotation | no comment; claimed as +40 m/s |
| `Delta_v` computed = 0.96 m/s | stated and used in axis | stated only | absent/wrong |

## Milestone 2 — Beam pattern (Week 3)

Truth for M=4, d=λ/2, θ_s = 20°: main lobe centered on 20°, CBF coherent
gain 4 (`sum(w*a_t) = 4`), sidelobes ≤ −13.3 dB (uniform window,
4-element array).

| Criterion | P | P- | R |
|---|---|---|---|
| Main lobe centered on steer angle (±1°) | yes | ±2° | off / no pattern |
| Sidelobe level ≤ −13 dB | yes | within +2 dB | above |
| Capon vs Bartlett contrast (L3) | two patterns shown, resolution difference stated | one pattern only | neither |
| (Week 4) Null ≥ 40 dB at −30°; unit gain at +20° | `w^H a_t = 1.0`, `w^H a_i ≈ 0` (verified) | null 30–40 dB | < 30 dB or no verification |

## Milestone 3 — Tracking plot (Week 2)

| Criterion | P | P- | R |
|---|---|---|---|
| True / measured / Kalman distinguishable (3 curves, legend) | 3 labeled | 2 visible | unclear |
| Track smoother than measurements, no systematic lag | visibly, no offset | small offset explained | lag or noisier than truth |
| Q/R reasoning (quiz Q8) in caption | both stated with effect | one stated | none |

## Milestone 4 — GNU Radio RD map (Week 5)

Truth: `radar_doppler.grc` with implemented epy blocks gives the same
target cell as the Python sim for (1000 m, 40 m/s).

> The learner-facing gate for this milestone is the **`03-hardware.md` §5
> validation checklist** — it must be fully ticked. The criteria below are
> the grading view of that same checklist; `06-training.md` §7 (GNU Radio)
> is the learner's self-check.

| Criterion | P | P- | R |
|---|---|---|---|
| Target cell matches Python sim (≤1 bin per axis) | yes | 1 bin on one axis | mismatch unexplained |
| All three flowgraphs run end-to-end sim-only | 3/3 | 2/3 | < 2 |
| Learner can map each block to its Python equivalent | all mapped | most | few/none |
| `03-hardware.md` §5 checklist fully ticked | all boxes | one unticked, explained | >1 unticked |

## Portfolio artifacts (06-training.md §8)

Each artifact = plot + config + 3–5 line caption. P requires: config
reproducibly regenerates the plot, caption states *what it shows, the key
number, the takeaway*. Any missing element → P-.

## Scoring rollup

- All criteria **P** → milestone done.
- Any **P-** → fix on the spot, log in the milestone note.
- Any **R** → redo the milestone (the roadmap's "verification is green"
  gate means tests must pass again too).