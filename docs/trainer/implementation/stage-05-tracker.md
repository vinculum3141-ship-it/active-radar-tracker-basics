# Stage 5 — Kalman tracking

## In one sentence

The range-Doppler map gives noisy detections; a Kalman filter blends those
measurements with a constant-velocity motion model to produce a smooth track
whose error is well below the raw sensor noise.

## The problem

Stages 3–4 give us, per CPI, a **detection**: a range (±7.5 m bin) and a
velocity (±0.96 m/s bin), both with sensor noise. A single detection is jumpy —
plot the raw measurements and they scatter around the truth. The Week 2
milestone wants a **tracked** curve (true / measured / tracked) that is visibly
smoother than the dots.

So:
1. **Measurements are noisy.** Each CPI's detection wanders around the true
   trajectory.
2. **We know the motion model.** A target moving at roughly constant velocity
   shouldn't teleport between CPIs.
3. **We want one smooth estimate** per CPI that beats any single measurement.

The Kalman filter does exactly this: it keeps a state estimate and its
uncertainty (`P`), predicts forward with the motion model, then corrects with
the new measurement, weighting each by its trust (`Q` vs `R`).

**Deliverable:** `tracker.py` (`KalmanTracker`, `State`) + `viz.plot_track`,
and `tests/test_tracker.py`.

## Approach — the algorithm in words

1. **State** `x = [range, velocity]`.
2. **Predict** (per CPI, advancing by `dt`): `x ← F·x`, `P ← F·P·Fᵀ + Q`,
   with `F = [[1, dt],[0, 1]]` (constant velocity).
3. **Update** with the CPI's `Detection` (range ± velocity): `K = P·Hᵀ(H·P·Hᵀ +
   R)⁻¹`, `x ← x + K(z − Hx)`, `P ← (I − KH)P`, with `H = I`.
4. **Accumulate** the corrected state into `track` for plotting.

`Q` = how wrong the model can be (process noise); `R` = how noisy the
detections are (measurement noise). The filter blends them automatically.

## What we built

`src/radar/tracker.py` per the API spec (`04-python-discipline.md` §3):

| Algorithm step | Function |
|---|---|
| 1 · state | `State(range_m, velocity_mps)` |
| 2 · predict | `KalmanTracker.predict()` |
| 3 · update | `KalmanTracker.update(measurement)` (takes a `Detection`) |
| 4 · history | `KalmanTracker.track` (property, `list[State]`) |

Plus `viz.plot_track(true, measured, cognitive?, track)` — true/measured/tracked
range *and* velocity, two panels.

**Files touched:** `src/radar/tracker.py`, `src/radar/viz.py`,
`tests/test_tracker.py`.

The measurement can carry range only, velocity only, or both — `update` builds
`H`/`z`/`R` from whatever `Detection` fields are present (so a range-only radar
still tracks; velocity is then inferred by the model).

## Physics in play

- **Constant-velocity model** (§5): `x_{k+1} = F x_k`, `F = [[1, dt],[0,1]]`.
- **Measurement model:** `z = H x + w`, `H = I` (we measure both range and
  velocity).
- **Kalman update** (§5): predict `P`, gain `K`, correct `x` and `P`. The gain
  is the relative-trust dial — high `K` trusts the sensor, low `K` trusts the
  model.

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| State | `[range, velocity]` | §5; 1-D radial track, the minimum that captures motion |
| `H = I` by default | measure range **and** velocity | RD map yields both; velocity-only/range-only also accepted |
| `Q`, `R` scalar → diagonal | `Q = q·I`, `R = r·I` | API takes scalar `q`, `r`; isotropic noise assumption |
| Per-measurement `H` | built from present `Detection` fields | robust to range-only or velocity-only detections |
| Seed state from 1st measurement | `x ← [range, velocity]` on first `update` | avoids a huge initial jump; transient is discarded in tests anyway |
| `track` accumulates post-update states | property | one `State` per CPI, in order, for plotting/tests |

Rejected: a richer motion model (acceleration/`CA`) — not needed for the
constant-velocity baseline (YAGNI); a fixed `H=I` only (would reject
range-only detections, which a real radar commonly has).

## Implementation

```python
def predict(self):
    self.x = self.F @ self.x
    self.P = self.F @ self.P @ self.F.T + self.Q
    return State(*self.x)


def update(self, m: Detection):
    if not self._track:  # seed from first measurement
        self.x = np.array([m.range_m or 0.0, m.velocity or 0.0])
    z, H = [], []
    if m.range_m is not None:
        z.append(m.range_m)
        H.append([1, 0])
    if m.velocity is not None:
        z.append(m.velocity)
        H.append([0, 1])
    z = np.array(z)
    H = np.array(H)
    R = np.eye(len(z)) * self.r
    S = H @ self.P @ H.T + R
    K = self.P @ H.T @ np.linalg.inv(S)
    self.x = self.x + K @ (z - H @ self.x)
    self.P = (np.eye(2) - K @ H) @ self.P
    self._track.append(State(*self.x))
    return self._track[-1]
```

## Key numbers

| Quantity | Value (test config) | Source |
|---|---|---|
| `dt` between CPIs | `0.1 s` | chosen for a clear run |
| Measurement noise `σ` | `5.0` (m, m/s) → `r = 25` | synthetic sensor model |
| Process noise `q` | `2.0` | tuned: model slightly fallible |
| Steady-state RMS range | `< 5 m` (≈ σ/2–σ/3) | test |
| Steady-state RMS velocity | `< 5 m/s` | test |
| Track RMS vs raw meas RMS | track **below** raw | the filter earns its keep |

## Verification

- `uv run pytest tests/test_tracker.py` → **5 passed**.
- `uv run ruff check .`, `uv run ruff format --check .` → clean.
- Full suite: **44 passed** (stages 1–5). Week 2 milestone (RD map + tracking
  plot + `test_doppler` + `test_tracker`) now complete.

### Why these 5 tests

| Test | Verifies | Why it matters |
|---|---|---|
| `test_api_shape` | `predict`/`update` return `State`; `track` is `list[State]` | the API contract (§3) |
| `test_range_only_accepted` | `velocity=None` still updates | robustness to range-only detections |
| `test_steady_state_error_below_measurement_noise` | RMS(range), RMS(vel) `< σ` | roadmap: "steady-state RMS track error below the measurement-noise bound" |
| `test_track_smooths_measurements` | track RMS `<` raw measurement RMS | proves the filter adds value, not just a rename |
| `test_converges_on_constant_velocity` | mean tracked vel ≈ true within 1 m/s | "converges on const-velocity target" |

Method note: tests use synthetic noisy detections (truth ± `σ`, seeded) — the
"measurement" is the sensor output, modeled directly. This tests the filter
against an analytic truth, per `04-python-discipline.md` §4, and stays fast and
deterministic.

## Gotchas / stretch notes

- **`Q` too big** → `K` trusts the sensor → the track **jitters** (follows noise).
  Demonstrated: `q = 1e3` gives a tracked-velocity std several× the `q = 2`
  case.
- **`R` too big** → `K` trusts the model → the track is **sluggish / lags**,
  especially through transients. Demonstrated: `r = 1e4` leaves a persistent
  velocity offset at startup.
- **Transient vs steady state.** The first ~15 CPIs carry the largest error;
  tests discard them (`k0 = 20`) and check the steady state.
- **Stretch (roadmap ◇):** two targets `(400 m, 15 m/s)` and `(1200 m, −20
  m/s)` → two *independent* `KalmanTracker`s (one per detection stream); plus
  the `Q`/`R` mis-tuning demo above to feel lag vs noise. Multi-target
  *data-association* (which detection belongs to which track) is deliberately
  out of scope here.

## Slide-ready takeaway

- The Kalman filter keeps `x = [range, velocity]` and its uncertainty `P`, then
  **predicts** with the constant-velocity model and **updates** with each CPI's
  noisy detection — blending model and sensor by their relative trust (`Q`/`R`).
- Result: a track whose steady-state error (`< 5 m`, `< 5 m/s`) sits **below**
  the raw measurement noise — the dots scatter, the line is smooth.
- Tuning is the craft: **big `Q` → jittery** (trusts sensor), **big `R` →
  sluggish** (trusts model). Two targets → two independent trackers.
