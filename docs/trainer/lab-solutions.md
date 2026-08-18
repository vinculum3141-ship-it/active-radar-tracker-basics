# Trainer — Lab Solutions

Instructor key for `docs/training/06-training.md` §6 (hands-on labs).
Each lab extends a roadmap stage. Give credit for the *investigation*
(they changed one thing, kept everything else fixed, recorded a number)
plus the conclusion below.

**Shared setup:** `cfg = RadarConfig()` from `src/radar/config.py`
(20 MHz fs, 5 MHz chirp, PRI 1 ms, N=64 pulses, target R=1000 m). Tests
and helpers from `04-python-discipline.md` §4.

## L1 — SNR sweep (Week 1)

**Task:** sweep SNR 30→0 dB, find where `detect_peaks` fails.

**Expected result:** failure (missed or extra detection) somewhere in the
~10–15 dB band for a fixed false-alarm threshold. The exact crossover moves
with the detection threshold — that's the point: detection SNR depends on
the threshold policy (`P_fa`), which is the CFAR idea previewed in
`08-extensions.md`.

**Method check:** one target, one config at a time; noise seed fixed; count
missed/false peaks across ≥ 20 trials per SNR; plot detection error vs SNR.

## L2 — PRF doubling (Week 2)

**Task:** double PRF (PRI 1 ms → 0.5 ms) and rerun Doppler for the 40 m/s
target.

**Expected result:** `v_max = lambda/(4·T)` doubles to **61.2 m/s**, so 40 m/s
is no longer ambiguous. The peak that was folded to -21.2 m/s now appears at
its true +40 m/s bin. Velocity estimate is consistent across runs (same bin
every run, seeded).

**Teaching point to confirm:** velocity ambiguity is a *sampling* problem in
slow time; raising PRF fixes it at the cost of a shorter unambiguous range.

## L3 — Angular resolution (Week 3)

**Task:** two targets 10° apart; Bartlett then Capon; measure peak
separation.

**Expected result:** for M=4, d=λ/2 the Bartlett (conventional) beam width is
~ λ/(M·d) ≈ 28.6°, so two targets 10° apart merge into one lobe. Capon with a
well-estimated covariance separates them (two resolvable peaks). 

**Method check:** one target at +5°, one at −5° (10° apart), equal power;
compare beam patterns; report peak locations. If Capon fails, the
covariance was rank-deficient (needs more snapshots / averaging).

## L4 — Adaptive nulling (Week 4)

**Task:** drift the interferer −30°→−20°; recompute LCMV weights per CPI.

**Expected result:** the null follows the interferer (new weights each CPI,
null at the measured angle) while the target response stays at ~unit gain.
Before/after range-Doppler maps show the interferer floor dropping by
40+ dB in the nulled run.

**Method check:** store `w` per CPI; the target constraint `w^H a(theta_t)=1`
must hold for every weight set. Use `grc/gen_weights.py` values to sanity
check the first CPI.

## L5 — Python vs GNU Radio cross-check (Week 5)

**Task:** same `(R=1000 m, v=40 m/s)` through the Python sim and
`radar_doppler.grc`; overlay results.

**Expected result:** target cell matches to within a bin on both axes
(range bin ~133, Doppler bin consistent with the aliased −21 m/s because
40 m/s > v_max). This requires the learner's `radar_taps`/epy implementations
(`grc/README.md`) to match `src/radar/signal_gen.py`.

**Method check:** both runs use the same fs/PRI/taps; report the (range,
Doppler) bin pair from each and the difference.

## Common failure modes

| Symptom | Cause to check |
|---|---|
| Echo peak not at 133 samples | `n_delay`/fs mismatch; matched taps not time-reversed |
| No Doppler shift visible | phase ramp applied to wrong path, or ramp step = 0 |
| Doppler peak at wrong sign/bin | forgot fftshift; v folded through ±v_max |
| Bartlett only shows one lobe at 10° | correct — that's the expected resolution limit |
| Capon null off-angle | covariance from too few snapshots, or `R` not inverted correctly |
| GRC target cell differs from sim | epy `range_doppler` reshape/FFT axis wrong |