# 04 — Python Coding Discipline

The code spec the roadmap (`05-roadmap.md`) implements. Written so the code
pass is mechanical: every module, its API, the conventions, and the tests are
fixed here.

---

## 1. Environment & tooling

- **`uv`** for project/dependency management:
  - macOS: `brew install uv`
  - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or your package
    manager, e.g. `apt install uv` on Debian/Ubuntu)
- Python **3.11+**.
- Dependencies: `numpy`, `scipy`, `matplotlib`, `pytest`, `ruff`, `pyproject.toml`.

```toml
[project]
name = "radar"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy", "scipy", "matplotlib"]

[dependency-groups]
dev = ["pytest", "ruff"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/radar"]
```

Layout:

```
src/radar/
  __init__.py
  config.py
  signal_gen.py
  channel.py
  receiver.py
  doppler.py
  tracker.py
  array.py
  beamformer.py
  viz.py
  cli.py
tests/
  test_signal_gen.py
  test_channel.py
  test_receiver.py
  test_doppler.py
  test_tracker.py
  test_array.py
  test_beamformer.py
```

Commands:

```bash
uv sync --dev          # install
uv run pytest          # test
uv run ruff check .    # lint
uv run ruff format .   # format
uv run radar bench     # CLI entry point
```

---

## 2. Conventions

- **NumPy-style docstrings** on every public function/class.
- **Type hints** on all signatures (`float`, `np.ndarray`, `dataclasses`).
- **Dataclasses** for config and data objects (`Detection`, `State`).
- No type-ignores, no unused imports (ruff enforces).
- Vectorized NumPy; avoid explicit loops over samples where possible.
- Units always stated in variable names or docstrings (`range_m`, `velocity_mps`,
  `fs_hz`).
- Fixed **RNG seed** everywhere so results are reproducible:
  `rng = np.random.default_rng(seed)` — never the global `np.random`.
- Plots are produced by `viz.py` only; simulations never plot by default
  (enabled via CLI flag). Keeps `pytest` runnable headless.

---

## 3. Module API spec

### `config.py`

```python
@dataclass
class RadarConfig:
    fc_hz: float = 2.45e9
    bandwidth_hz: float = 5e6
    pulse_width_s: float = 20e-6
    pri_s: float = 1e-3
    fs_hz: float = 20e6
    n_pulses: int = 64
    pulse_type: str = "lfm"          # "rect" | "lfm"
    target_range_m: float = 1000.0
    target_velocity_mps: float = 40.0
    snr_db: float = 20.0
    seed: int = 42
    n_elements: int = 4              # stages 6+
    array_spacing_lambda: float = 0.5
    target_angle_deg: float = 20.0
    interferer_angle_deg: float = -30.0   # stages 8+

def load_config(path: str | None = None) -> RadarConfig: ...
```

### `signal_gen.py`

```python
def rectangular_pulse(cfg: RadarConfig) -> np.ndarray: ...
def lfm_chirp(cfg: RadarConfig) -> np.ndarray: ...          # complex analytic
def pulse_train(cfg: RadarConfig) -> np.ndarray: ...        # [n_pulses, samples]
def transmit_waveform(cfg: RadarConfig) -> np.ndarray: ...
```

### `channel.py`

```python
@dataclass
class Target:
    range_m: float
    velocity_mps: float
    angle_deg: float | None = None
    snr_db: float = 20.0

def propagate(pulse: np.ndarray, target: Target, cfg: RadarConfig, rng) -> np.ndarray: ...
def simulate_channel(tx: np.ndarray, targets: list[Target], cfg, rng) -> np.ndarray: ...
```

### `receiver.py`

```python
def matched_filter(rx: np.ndarray, tx_pulse: np.ndarray) -> np.ndarray: ...
def range_from_delay(delay_samples: int, cfg: RadarConfig) -> float: ...
def detect_peaks(matched: np.ndarray, cfg, threshold_db: float = 10.0) -> list[Detection]: ...
```

### `doppler.py`

```python
def range_doppler_map(matched: np.ndarray, cfg: RadarConfig) -> np.ndarray: ...
def range_axis(cfg) -> np.ndarray: ...
def velocity_axis(cfg) -> np.ndarray: ...
```

### `tracker.py`

```python
@dataclass
class State: range_m: float; velocity_mps: float

class KalmanTracker:
    def __init__(self, dt_s: float, q: float, r: float): ...
    def predict(self) -> None: ...
    def update(self, measurement: Detection) -> State: ...
    @property
    def track(self) -> list[State]: ...
```

### `array.py` (stages 6+)

```python
def steering_vector(theta_deg: float, n_elements: int, spacing_lambda: float) -> np.ndarray: ...
def array_response(x: np.ndarray, theta_deg: float, cfg) -> np.ndarray: ...
def beam_pattern(weights: np.ndarray, thetas_deg: np.ndarray, cfg) -> np.ndarray: ...
```

### `beamformer.py` (stages 7+)

```python
def bartlett_scan(array_data: np.ndarray, thetas_deg: np.ndarray, cfg) -> np.ndarray: ...
def capon_weights(array_data: np.ndarray, theta_deg: float, cfg) -> np.ndarray: ...
def lcmv_weights(array_data: np.ndarray, target_deg: float, interferer_deg: float, cfg) -> np.ndarray: ...
def apply_weights(array_data: np.ndarray, weights: np.ndarray) -> np.ndarray: ...
```

### `viz.py`

```python
def plot_pulse(tx: np.ndarray, cfg): ...
def plot_echo(rx: np.ndarray, matched: np.ndarray, cfg): ...
def plot_range_profile(matched: np.ndarray, cfg): ...
def plot_rd_map(rd_map: np.ndarray, cfg): ...
def plot_track(true: list, measured: list, track: list): ...
def plot_beam_pattern(thetas_deg: np.ndarray, pattern: np.ndarray): ...
def plot_array_geometry(cfg): ...
```

### `cli.py`

```python
def main() -> None: ...
# subcommands: simulate, bench, plot, track
```

```bash
uv run radar simulate --config configs/baseline.yaml --plot
uv run radar track --n-targets 2 --plot
uv run radar bench            # timing + numerical checks
```

---

## 4. Testing discipline

Every stage in the roadmap ships with tests. The verification philosophy:
**test against analytical answers, not against the previous run.**

| Module | Test verifies |
|---|---|
| `test_signal_gen` | chirp starts/ends at expected frequencies; pulse length correct |
| `test_channel` | echo appears at `2R/c` delay; noise scales with SNR |
| `test_receiver` | matched filter peak at expected delay; range error < 1 bin |
| `test_doppler` | peak Doppler bin → velocity within `Δv/2`; map dimensions |
| `test_tracker` | steady-state tracking error below bound; converges on const-velocity target |
| `test_array` | steering vector phase matches `2π d sinθ/λ`; beam pattern peak at target angle |
| `test_beamformer` | LCMV: `wᴴ a(θi) ≈ 0`, `wᴴ a(θt) ≈ 1`; null depth > 40 dB |

Test hygiene:

- All tests `seeded`; no network, no display.
- Numerical tolerances explicit (`pytest.approx`, `rtol/atol`).
- One test file per module; fixtures for a `RadarConfig` with tiny dimensions
  to keep CI fast.

---

## 5. Reproducibility & documentation

- Every script/CLI run prints the `RadarConfig` used (hashable, diffable).
- Plots are saved to `out/<stage>/<name>.png` when `--plot` is given.
- Config lives in `configs/*.yaml` for experiments; defaults in code stay
  aligned with `config.py`.
- A `README.md` change note per stage, plus a `notebooks/` (optional) for
  exploration — never for the shipped pipeline.