# 05 — Roadmap

A **5-week** staged implementation plan. Each stage has an objective, the
physics it exercises, the code task (against the spec in
`04-python-discipline.md`), and a **verification** you must see before moving
on. Stages build on each other; each week ends in a demonstrable milestone.

> Pace yourself: if a week's verification is green, that week is done — even
> if the "stretch" items are skipped. Come back later; the stages are
> deliberately order-independent once complete.
>
> Overall completion (the point where the whole course is done) is defined
> once, in `06-training.md` §9 "Definition of done".

Legend: **✓ = must-have** · **◇ = stretch**

---

## Week 1 — Pulse radar + range estimation (stages 1–3)

### Stage 1 · Radar waveform
- **Objective:** generate the transmit waveform — rectangular pulse, then LFM chirp.
- **Physics:** `01-physics.md` §1, §3 (pulse parameters, chirp, range resolution).
- **Code task:** `signal_gen.py` (`rectangular_pulse`, `lfm_chirp`,
  `transmit_waveform`). `config.py` is provided: the `RadarConfig`
  dataclass, `load_config`, `config_summary` and the `configs/` folder
  are skeleton (04-python-discipline.md §5).
- **Verification:** `test_signal_gen` green; chirp frequency sweep
  `f0→f1` spans `B`; plot of `pulse` shows `τ = 20 us` at `fs = 20 MHz`.
- **◇** Pulse-compression preview: autocorrelate the chirp
  (`scipy.signal.correlate`, `mode="same"`) and plot the magnitude.
  `correlate` conjugates its kernel, so correlating the chirp with itself
  *is* a matched filter. Measure the peak-to-first-null half-width (expect
  `1/B` = 0.2 us, 4 samples) and the compression ratio (pulse samples ÷
  half-width ≈ `tau*B` = 100). Self-contained — uses only the Stage 1 chirp;
  this is the mechanism behind Q4's `ΔR = c/(2B)`.

### Stage 2 · Moving target simulation
- **Objective:** a channel that turns a pulse into a delayed, attenuated,
  noisy echo for a moving target.
- **Physics:** `01-physics.md` §1 (range–delay, range equation), §4 intuition.
- **Code task:** `channel.py` (`Target`, `propagate`, `simulate_channel`).
- **Verification:** `test_channel` green; echo peak lands at
  `round(2·R/c·fs)`; noise power matches `SNR`.
- **◇** Two targets in `simulate_channel`.

### Stage 3 · Range estimation (matched filter)
- **Objective:** extract target range from the echo via correlation.
- **Physics:** `01-physics.md` §2, §3 (matched filtering, `R = c·τ/2`).
- **Code task:** `receiver.py` (`matched_filter`, `range_from_delay`,
  `detect_peaks`), `viz.py` (`plot_echo`, `plot_range_profile`).
- **Verification:** `test_receiver` green; measured range within one range
  bin of truth at `SNR = 20 dB`; matched-filter peak visibly sharper than the
  echo.
- **◇** `detect_peaks` handles two targets; report `SNR` per detection.

### Week 1 milestone
A plot set (pulse, echo, matched-filter output, range profile) and a passing
`test_signal_gen` + `test_channel` + `test_receiver`.

---

## Week 2 — Doppler + tracking (stages 4–5)

### Stage 4 · Doppler / velocity (range-Doppler map)
- **Objective:** stack pulses, FFT along slow time, produce a range-Doppler map
  and velocity axis.
- **Physics:** `01-physics.md` §4 (`v = λf_d/2`, resolution, ambiguity).
- **Code task:** `doppler.py` (`range_doppler_map`, `range_axis`,
  `velocity_axis`), `viz.py` (`plot_rd_map`).
- **Verification:** `test_doppler` green; peak cell for `R=1000 m, v=40 m/s`
  within `Δv/2`; the 2-D map shows the target blob.
- **◇** Raise `v` above `v_max` and observe/explain aliasing; add a window
  along slow time.

### Stage 5 · Kalman tracking
- **Objective:** smooth noisy detections into a track over time.
- **Physics:** `01-physics.md` §5 (predict/update, `Q`/`R`).
- **Code task:** `tracker.py` (`KalmanTracker`), `viz.py` (`plot_track`).
- **Verification:** `test_tracker` green; steady-state RMS track error
  below the measurement-noise bound; plot shows true/measured/tracked curves.
- **◇** Multi-target: two `Target`s at `(400 m, 15 m/s)` and
  `(1200 m, -20 m/s)`, independent tracks; try `Q`/`R` mis-tuning and observe
  lag vs. noise.

### Week 2 milestone
A range-Doppler map and a tracking plot over a run of pulses; passing
`test_doppler` + `test_tracker`. First portfolio artifact: the range-Doppler
map.

---

## Week 3 — Array + DOA (stages 6–8)

### Stage 6 · 4-element antenna array
- **Objective:** model a ULA, compute steering vectors, plot the array's beam
  pattern and geometry.
- **Physics:** `01-physics.md` §6 (phase offsets, `a(θ)`, grating lobes).
- **Code task:** `array.py` (`steering_vector`, `array_response`,
  `beam_pattern`), `viz.py` (`plot_array_geometry`, `plot_beam_pattern`).
- **Verification:** `test_array` green; pattern peak at the steer angle;
  steering-vector phases match `2π d sinθ/λ`.
- **◇** Vary `d/λ` and show grating lobes appear when `d > λ/2`.

### Stage 7 · Direction-of-arrival
- **Objective:** estimate angles from array snapshots (Bartlett, then Capon).
- **Physics:** `01-physics.md` §7.
- **Code task:** `beamformer.py` (`bartlett_scan`, `capon_weights`).
- **Verification:** Bartlett finds the true target angle; Capon resolves
  two close angles that Bartlett cannot.
- **◇** Compare Bartlett vs Capon peak width for two targets 10° apart.

### Stage 8 · Interference source
- **Objective:** add a strong interferer at a known angle and show it masks the
  target in the range-Doppler map.
- **Physics:** `01-physics.md` §8 (interference, masking).
- **Code task:** `channel.py` extension for an interferer `Target`; `viz.py`
  `plot_rd_map` before/after.
- **Verification:** with interferer `(-30°, high power)`, the target at `+20°`
  is no longer cleanly detectable in the RD map.
- **◇** Interferer with the same Doppler as the target — masking is worst
  when they overlap in Doppler.

### Week 3 milestone
Array geometry + beam-pattern plot and a DOA result; passing `test_array` +
`test_beamformer` (Bartlett/Capon). Second portfolio artifact: the beam
pattern.

---

## Week 4 — Adaptive null steering (stages 9–11)

### Stage 9 · Beam steering
- **Objective:** steer the beam at the target using `w = a(θ_t)`, verify gain.
- **Physics:** `01-physics.md` §6–7.
- **Code task:** `beamformer.py` (`apply_weights`), wiring array → beamformer
  → receiver in the pipeline.
- **Verification:** `wᴴ a(θ_t) ≈ M` (coherent gain); target SNR improves in the
  RD map after steering.
- **◇** Plot gain-at-target vs. steering error (sensitivity curve).

### Stage 10 · Adaptive null (LCMV)
- **Objective:** place a null on the interferer while keeping unit gain at the
  target, via `w_lcmv`.
- **Physics:** `01-physics.md` §8 (LCMV constraint `Cᴴw = g`).
- **Code task:** `beamformer.py` (`lcmv_weights`).
- **Verification:** `test_beamformer` green — null depth at `θ_i` > 40 dB,
  unit gain at `θ_t`; plot the pattern showing both lobe and null.
- **◇** Derive and verify `w = R̂⁻¹C(CᴴR̂⁻¹C)⁻¹g` against a brute-force
  constrained optimizer.

### Stage 11 · Range-Doppler after cancellation
- **Objective:** reprocess the nulled array output; the target is visible again.
- **Physics:** `01-physics.md` §8 (result).
- **Code task:** end-to-end pipeline wiring; `viz.py` before/after RD maps.
- **Verification:** target detectable at `+20°` with interferer `(-30°)`
  suppressed; RD map after nulling matches the no-interferer case closely.
- **◇** Moving interferer: drift `θ_i` from `-30°→-20°` and recompute weights
  per CPI; plot null following the interferer.

### Week 4 milestone
Beam pattern with main lobe + deep null; before/after RD maps. Third portfolio
artifact: the adaptive-null antenna pattern and the cancellation result.

---

## Week 5 — GNU Radio port (stage 12)

### Stage 12 · GNU Radio flowgraphs
- **Objective:** re-express TX/RX/Doppler chains as GRC flowgraphs, running
  sim-only; verify against the Python sim.
- **Architecture:** `02-architecture.md` §3, `03-hardware.md` §2.
- **Code task:** `radar_tx.grc`, `radar_rx_sim.grc`, `radar_doppler.grc`
  (array variant optional); taps exported from Python.
- **Verification:** matched-filter peak at the same delay as the Python sim;
  range-Doppler map shows the same target cell for the `(R, v)` test case.
- **◇** Array/beamformer flowgraph with LCMV weights; hardware swap notes
  applied to `osmocom` sources/sinks.

### Week 5 milestone
Three working flowgraphs producing the same numbers as the Python pipeline;
full `03-hardware.md` validation checklist passed. Fourth portfolio artifact:
a GNU Radio screenshot of the range-Doppler map.

---

## Summary table

| Week | Stages | Capability | Artifact |
|---|---|---|---|
| 1 | 1–3 | Waveform, channel, matched-filter range | Range profile |
| 2 | 4–5 | Range-Doppler, Kalman tracking | Range-Doppler map |
| 3 | 6–8 | ULA, DOA, interference | Beam pattern |
| 4 | 9–11 | Beam steering, LCMV null, cancellation | Null pattern + before/after |
| 5 | 12 | GNU Radio port, hardware-mapped | GNU Radio RD map |