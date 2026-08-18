# GNU Radio Flowgraphs

Teaching skeleton for the active radar tracker. These flowgraphs are the
"hardware path" reference for `docs/training/03-hardware.md`. They are
**not finished programs** — the radar DSP lives in the embedded Python
blocks, which are left as `NotImplementedError` stubs for the learner to
implement (same deal as `src/radar/`).

Requires GNU Radio **3.10** (GRC). Validate that the YAML parses and the
embedded Python compiles with:

    uv run python -c "import yaml,glob;[yaml.safe_load(open(f)) for f in glob.glob('grc/*.grc')]"

Opening a flowgraph in gnuradio-companion and generating it will fail
until the embedded Python stubs are implemented — that is intentional.

## Files

| File | Doc section | Provided (plumbing) | Learner implements |
|---|---|---|---|
| `radar_tx.grc` | 03-hardware.md 2.1 | vector source (repeat), throttle, time/freq sinks | `chirp()`, `pulse_vector()` in the `radar_taps` epy module |
| `radar_rx_sim.grc` | 03-hardware.md 2.2 | delay, noise, add, FIR, complex->mag, sinks | `matched()` (FIR taps) + `pulse_vector()` |
| `radar_doppler.grc` | 03-hardware.md 2.3 | vector source, delay, leakage+noise add, FIR, keep_m_in_n, raster sink | `matched()` + `doppler_phase.work()` + `range_doppler.general_work()` |
| `radar_array.grc` | 03-hardware.md 2.4 | 4 element chains, arrival phases, steering weights, combine, FIR, sinks | `matched()` |
| `gen_weights.py` | — | regenerate the arrival/steering/LCMV constants below | — |

The `radar_taps` epy module (in every flowgraph) mirrors
`src/radar/signal_gen.py`; the `doppler_phase` and `range_doppler` epy
blocks mirror `src/radar/channel.py` / `src/radar/doppler.py`. Learners
implement the Python package first, then port the same math into these
blocks.

## Test-case constants

The flowgraphs hard-code the "R=1000 m, v=40 m/s, theta=20 deg" test cases
from `docs/training/01-physics.md` / `03-hardware.md`:

- Sampling rate 20 MHz, PRI 1 ms, pulse 20 us (2% duty).
- **Delay**: `n_delay = round(2R/c * fs) = 133` samples (R=1000 m).
- **Doppler**: `f_d = 2v/lambda = 653.33 Hz`, per-pulse phase
  `2*pi*f_d*PRI = 4.1050144006906635 rad`. Note v=40 m/s exceeds the
  unambiguous velocity `v_max = lambda/(4*PRI) = 30.6 m/s`, so the peak
  aliases — a deliberate teaching point.
- **Array** (4-element half-wave ULA, theta_t=20 deg): arrival phases
  `[0, 1.0745, 2.1490, 3.2235]` rad; CBF steering weights are the
  conjugates (`sum(w*a_t) = 4`). LCMV nulling weights for an interferer
  at -30 deg satisfy `w^H a_t = 1`, `w^H a_i = 0`.

Regenerate/check them with:

    uv run grc/gen_weights.py

## GRC 3.10 format notes

- `.grc` files are YAML: `options` / `blocks` / `connections` / `metadata`.
- Embedded Python is stored as a plain YAML literal block (`|-`) in
  `epy_module.source_code` and `epy_block._source_code`.
- Custom `epy_block` parameters (from the class `__init__` defaults) are
  serialized in the YAML with their values — GRC needs them present to
  generate the block's constructor call. Keep them in sync with the
  `__init__` defaults in `_source_code`.
- `epy_module` generated module names are `{flowgraph_id}_{name}`
  (e.g. `radar_tx_radar_taps`), imported as `{name}`.

## Validation checklist (03-hardware.md section 5)

- [ ] `radar_tx`: time sink shows a 20 us chirp every 1 ms PRI.
- [ ] `radar_rx_sim`: compressed pulse peak at ~133 samples after the PRI
      start; range resolution ~30 m.
- [ ] `radar_doppler`: raster shows the echo at range bin ~133 and a
      Doppler peak (aliased because v > v_max); leakage stays at bin 0.
- [ ] `radar_array`: beamformer envelope ~4x a single element (~6 dB
      SNR gain over per-element noise).