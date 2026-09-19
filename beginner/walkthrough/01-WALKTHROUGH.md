# Walkthrough — 01: Pulse Generation and Chirp Intuition

This is a cell-by-cell walkthrough of `beginner/notebooks/01-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 01 — Pulse Generation and Chirp Intuition

This notebook shows how a plain rectangular pulse becomes a frequency-swept LFM chirp, and why that sweep gives a radar much better range resolution than the pulse length alone would allow.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/01-pulse-chirp-intuition.ipynb)

Use this link if you want to open the notebook in Colab and follow along in a browser notebook environment.

## What this notebook teaches

In Notebook 00 we treated the transmit burst as a simple time interval. Here we look inside that interval and build the actual waveform.

By the end of this notebook, you should be able to explain:

- what a rectangular pulse looks like in time,
- what an LFM chirp is and how its frequency sweeps,
- why a chirp can resolve targets much closer together than its pulse length suggests,
- and what the time-bandwidth product tells us about that advantage.

Keep these four questions in mind as you work through the cells. At the end of the notebook, a dedicated section answers each one directly, so you can study the material first and then check your understanding against the full story.

## Setup and baseline values

We reuse the baseline radar specification from Notebook 00 so every waveform here is built from the same physical case. If you are running in Colab, run the bootstrap cell below first so the repository is cloned, installed, and available for import.

### Notebook cell 4 · code
```python
import os
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/vinculum3141-ship-it/active-radar-tracker-basics.git"
BRANCH_NAME = "radar-tracker-notebooks"
REPO_DIR = Path("/content/active-radar-tracker-basics")

in_colab = "google.colab" in sys.modules

if in_colab and not REPO_DIR.exists():
    subprocess.run(
        ["git", "clone", "--branch", BRANCH_NAME, "--single-branch", REPO_URL, str(REPO_DIR)],
        check=True,
    )

if in_colab:
    os.chdir(REPO_DIR)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", "."], check=True)

    repo_root = os.path.abspath(".")
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    print(f"Ready in Colab from {REPO_DIR}")
else:
    repo_root = Path.cwd().resolve()
    for candidate in [repo_root, *repo_root.parents]:
        if (candidate / "beginner").exists() and (candidate / "pyproject.toml").exists():
            repo_root = candidate
            break
    repo_root = str(repo_root)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    print(f"Running locally from {repo_root}")
```

**Executed output:**

```
Running locally from /Users/ruby/Projects/active-radar-tracker-basics
```

**What this cell does — Prepare the environment.**

The same door as every notebook in this course. In Colab this cell clones the repository, installs the beginner package, and steps into the workspace. Running locally it simply locates the repo root, puts it on the import path, and prints the path so you can see where you are working.

You never need to edit this cell. Run it once; every following cell expects it to have run.

### Notebook cell 5 · code
```python
import numpy as np
import matplotlib.pyplot as plt

from beginner.helpers import BaselineRadarSpec, baseline_spec
from beginner.helpers.plotting import apply_notebook_style

# Set the shared notebook styling once for consistent plots.
apply_notebook_style()

# Create one named radar specification so the lesson reads naturally.
radar_spec = BaselineRadarSpec()
radar_spec
```

**Executed output:**

```
BaselineRadarSpec(fc_hz=2450000000.0, bandwidth_hz=5000000.0, pulse_width_s=2e-05, pri_s=0.001, fs_hz=20000000.0, n_pulses=64, target_range_m=1000.0, target_velocity_mps=40.0, snr_db=20.0, target_angle_deg=20.0, interferer_angle_deg=-30.0)
```

**What this cell does — Setup: one baseline spec for every waveform.**

Imports plus one named specification, the same BaselineRadarSpec object from Notebook 00: 2.45 GHz carrier, 5 MHz bandwidth, 20 microsecond pulse, 1 millisecond PRI, 20 MHz sampling rate, target at 1000 m. Every waveform in this lesson is built from this single object so the numbers stay consistent across notebooks.

The 5 MHz bandwidth on the second line is the key number here. It is the range of the chirp's frequency sweep, and later it is the bandwidth that sets range resolution after pulse compression.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## The rectangular pulse

The simplest transmit waveform is a rectangular pulse: the transmitter is simply on at full amplitude for the pulse width, then off. In sampled form it is just a block of ones.

The number of samples the pulse occupies is

$$
N = f_s \cdot \tau
$$

where $f_s$ is the sampling rate and $\tau$ is the pulse width. This block of energy is short in time, but its frequency content is broad only up to about $1/\tau$.

### Notebook cell 8 · code
```python
# Build the rectangular pulse directly so you can see the construction.
pulse_samples = int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))
rect_pulse = np.ones(pulse_samples, dtype=float)

print(f"Pulse width = {radar_spec.pulse_width_s * 1e6:.1f} microseconds")
print(f"Sampling rate = {radar_spec.fs_hz / 1e6:.1f} MHz")
print(f"Samples in one pulse N = {pulse_samples}")
```

**Executed output:**

```
Pulse width = 20.0 microseconds
Sampling rate = 20.0 MHz
Samples in one pulse N = 400
```

**What this cell does — The rectangular pulse, by hand.**

The plain pulse is exactly what its name says: the transmitter on at full amplitude for 20 microseconds, then off. In sampled form that is a block of 400 ones, from N = fs x tau = 20 MHz x 20 microseconds = 400 samples. No sweep, no hidden structure.

Keep the number 400 samples in mind. The chirp that follows occupies the same 400 samples but puts structure inside them.

## The LFM chirp

A linear-frequency-modulation (LFM) chirp keeps the same pulse length, but during the pulse the frequency sweeps linearly from a start value to a stop value. In the baseband form we use here, the instantaneous frequency rises from $0$ to the bandwidth $B$.

The complex baseband chirp is

$$
s(t) = \exp\!\left(j \pi \frac{B}{\tau} t^{2}\right)
$$

where the chirp rate $B/\tau$ sets how fast the frequency climbs. The key point is that the frequency range covered, $B$, can be much larger than $1/\tau$ — and that extra bandwidth is what buys us resolution later.

### Notebook cell 10 · code
```python
# Build the LFM chirp directly so you can see the quadratic phase formula.
t = np.arange(pulse_samples) / radar_spec.fs_hz
chirp_rate = radar_spec.bandwidth_hz / radar_spec.pulse_width_s
chirp_phase = np.pi * chirp_rate * t**2
chirp = np.exp(1j * chirp_phase)

# Estimate the instantaneous frequency from the phase slope.
inst_freq = np.diff(np.unwrap(np.angle(chirp))) / (2.0 * np.pi) * radar_spec.fs_hz

print(f"Chirp rate = {chirp_rate:.3e} Hz/s")
print(f"Start frequency = {inst_freq[0]:.2f} Hz")
print(f"Stop frequency = {inst_freq[-1] / 1e6:.2f} MHz (approximately the bandwidth)")
print(f"Bandwidth B = {radar_spec.bandwidth_hz / 1e6:.1f} MHz")
```

**Executed output:**

```
Chirp rate = 2.500e+11 Hz/s
Start frequency = 6250.00 Hz
Stop frequency = 4.98 MHz (approximately the bandwidth)
Bandwidth B = 5.0 MHz
```

**What this cell does — The LFM chirp, by hand.**

Inside the same 400 samples the phase grows quadratically: phase = pi x (B/tau) x t^2, with chirp rate B/tau = 2.5e11 Hz/s. The instantaneous frequency is the slope of the phase, so it climbs linearly, from near 0 Hz to 4.98 MHz across the pulse. That steady climb is what makes it a chirp.

The start is not exactly zero (6250 Hz, the first sample of a quadratic ramp) and the stop reads 4.98 MHz: the visible sweep spans the 5 MHz bandwidth. Notice B is far larger than 1/tau = 50 kHz, which is the entire point of the sweep.

## The two waveforms side by side

Plotted in time, the rectangular pulse is a flat block of ones. 
The chirp looks very different — its real and imaginary parts oscillate with a frequency that rises during the pulse. 
But if you look at the envelope (the absolute value), the chirp has the same constant-amplitude shape as the rectangular pulse. 
Both waveforms carry energy for the same duration; the difference is how that energy is distributed in phase.

### Notebook cell 12 · code
```python
# Show the time-domain shape of both waveforms.
fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)

axes[0].plot(t * 1e6, rect_pulse, color="#d95f02")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Rectangular pulse (flat in time)")

axes[1].plot(t * 1e6, np.real(chirp), color="#1b9e77", label="real part", alpha=0.6)
axes[1].plot(t * 1e6, np.imag(chirp), color="#7570b3", label="imaginary part", alpha=0.6)
axes[1].plot(t * 1e6, np.abs(chirp), color="black", linewidth=2, linestyle="--", label="envelope (abs)")
axes[1].set_ylabel("Amplitude")
axes[1].set_xlabel("Time within pulse (microseconds)")
axes[1].set_title("LFM chirp (oscillates, but envelope is flat like the pulse)")
axes[1].legend(loc="upper right")

plt.tight_layout()
plt.show()
```

**Executed output:**

```
<Figure size 1000x500 with 2 Axes>
```

![Notebook output](assets/01/fig_cell12_0.png)

**What this cell does — Both waveforms, one picture.**

Top: the rectangular pulse, a flat orange block of ones. Bottom: the chirp's real and imaginary parts oscillate with a frequency that rises through the pulse, while the black dashed envelope (absolute value) is flat, the same constant amplitude as the pulse.

Both waveforms carry energy for the same 20 microseconds. The only difference is how that energy is organized in phase - and that phase organization is the entire source of pulse compression.

## The frequency sweep

The chirp's defining feature is its linear frequency ramp. This is the plot that separates it from the plain pulse: the plain pulse has no sweep, while the chirp climbs steadily across the whole pulse width.

### Notebook cell 14 · code
```python
# Show the instantaneous frequency ramp of the chirp.
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(t[1:] * 1e6, inst_freq / 1e6, color="#1b9e77")
ax.axhline(radar_spec.bandwidth_hz / 1e6, color="#999999", linestyle="--", label="Bandwidth B")
ax.set_xlabel("Time within pulse (microseconds)")
ax.set_ylabel("Frequency (MHz)")
ax.set_title("Chirp instantaneous frequency sweeps 0 to B")
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()
```

**Executed output:**

```
<Figure size 1000x300 with 1 Axes>
```

![Notebook output](assets/01/fig_cell14_0.png)

**What this cell does — The frequency ramp.**

The defining plot of the notebook. The chirp's instantaneous frequency climbs linearly from near 0 to the 5 MHz bandwidth across the pulse, and the dashed line marks the bandwidth B. The plain pulse has no such ramp.

Keep this picture for the resolution section: the ramp is what assigns every instant in the pulse a unique frequency, and unique labels are what later make the chirp compress.

## Why chirps matter: range resolution

Range resolution is the smallest separation between two targets that the radar can tell apart. For a plain pulse it is set by the pulse length:

$$
\Delta R_{\text{pulse}} = \frac{c \, \tau}{2}
$$

For a pulse-compressed chirp it is set by the bandwidth:

$$
\Delta R_{\text{chirp}} = \frac{c}{2 B}
$$

Because $B \gg 1/\tau$, the chirp resolves targets far closer together than the raw pulse length would allow — the long pulse keeps the energy high while the bandwidth keeps the resolution sharp.

### Notebook cell 16 · code
```python
# Compare range resolution the two waveforms give, by hand.
c = 299_792_458.0
res_pulse = c * radar_spec.pulse_width_s / 2.0
res_chirp = c / (2.0 * radar_spec.bandwidth_hz)

print("Range resolution from the raw pulse length:")
print(f"  delta R_pulse = c * tau / 2 = {res_pulse:.1f} m")
print()
print("Range resolution after pulse compression by bandwidth:")
print(f"  delta R_chirp = c / (2B) = {res_chirp:.1f} m")
print()
print(f"Resolution improvement factor = {res_pulse / res_chirp:.1f}x")
```

**Executed output:**

```
Range resolution from the raw pulse length:
  delta R_pulse = c * tau / 2 = 2997.9 m

Range resolution after pulse compression by bandwidth:
  delta R_chirp = c / (2B) = 30.0 m

Resolution improvement factor = 100.0x
```

**What this cell does — Why chirps resolve better: the two formulas.**

Two formulas, one message. The plain pulse resolves c*tau/2 = 2997.9 m, nearly 3 km - too coarse for practical radar. The compressed chirp resolves c/(2B) = 30.0 m, a 100 times improvement. The improvement factor equals B*tau: since B is 100 times larger than 1/tau, the factor is exactly 100.

This is the arithmetic behind the claim that resolution is a bandwidth story, not a pulse-length story.

## The time-bandwidth product

The ratio

$$
TBP = B \cdot \tau
$$

is the time-bandwidth product. It measures how much the chirp squeezes a long pulse into a short compressed peak. A large time-bandwidth product means a long, energetic pulse can still give fine range resolution — the central trade that makes modern pulse radar practical.

### Notebook cell 18 · code
```python
# Compute the time-bandwidth product directly.
tbp = radar_spec.bandwidth_hz * radar_spec.pulse_width_s

print(f"Bandwidth B = {radar_spec.bandwidth_hz / 1e6:.1f} MHz")
print(f"Pulse width tau = {radar_spec.pulse_width_s * 1e6:.1f} microseconds")
print(f"Time-bandwidth product = {tbp:.0f}")
print()
print("The pulse is long in time, but the bandwidth compresses it by this factor.")
```

**Executed output:**

```
Bandwidth B = 5.0 MHz
Pulse width tau = 20.0 microseconds
Time-bandwidth product = 100

The pulse is long in time, but the bandwidth compresses it by this factor.
```

**What this cell does — The time-bandwidth product.**

TBP = B * tau = 5 MHz x 20 microseconds = 100. It is the compression ratio: how many times narrower the matched-filtered chirp peak will be than the raw pulse. A large TBP is how a long, energetic pulse still gives fine range resolution.

The summary to carry forward: long pulse for energy, wide bandwidth for sharpness, and the product says how much the two give you together.

## Checkpoint

In your own words, why can a chirp resolve targets closer together than a plain pulse of the same length?

Then answer this: if you increase the bandwidth $B$ while keeping the pulse width $\tau$ fixed, what happens to the time-bandwidth product and to the range resolution?

## Common mistake

A common mistake is to think the pulse length alone sets resolution. It does for a plain pulse, but a chirp decouples the two: the pulse can stay long (for energy) while the bandwidth sets the resolution. That is the whole point of pulse compression.

Another mistake is to read the chirp's time-domain plot as just "a weird pulse." The resolution lives in the frequency sweep, not in the amplitude shape, so always check the frequency view before judging a waveform.

## Why the helpers exist

The cells above show the quadratic phase and the resolution formulas directly so you can see the construction happen. After that first pass, those same operations move into the helper package so later notebooks can build waveforms and resolution numbers without repeating the derivation.

That is what the helper functions are for:

- they keep a single, correct waveform definition available to every later notebook,
- they reduce repeated code,
- and they make later lesson cells shorter once you already understand the idea.

As in Notebook 00, use the helpers when you want the lesson to stay readable, but keep the first occurrence of a concept visible in the notebook itself.

### Notebook cell 22 · code
```python
# Now use the helper functions to reproduce the same waveforms and numbers compactly.
from beginner.helpers import (
    lfm_chirp,
    rectangular_pulse,
    instantaneous_frequency_hz,
    range_resolution_from_pulse_width,
    range_resolution_from_bandwidth,
)

helper_spec = baseline_spec()
helper_n = int(round(helper_spec.pulse_width_s * helper_spec.fs_hz))
helper_rect = rectangular_pulse(helper_n)
helper_chirp = lfm_chirp(helper_n, helper_spec.bandwidth_hz, helper_spec.pulse_width_s, helper_spec.fs_hz)
helper_freq = instantaneous_frequency_hz(helper_chirp, helper_spec.fs_hz)
helper_res_pulse = range_resolution_from_pulse_width(helper_spec.pulse_width_s)
helper_res_chirp = range_resolution_from_bandwidth(helper_spec.bandwidth_hz)

print("Helper-based version of the same calculations:")
print(f"  samples per pulse = {helper_n}")
print(f"  sweep 0 -> {helper_freq[-1] / 1e6:.2f} MHz")
print(f"  pulse resolution = {helper_res_pulse:.1f} m")
print(f"  chirp resolution = {helper_res_chirp:.1f} m")
```

**Executed output:**

```
Helper-based version of the same calculations:
  samples per pulse = 400
  sweep 0 -> 4.98 MHz
  pulse resolution = 2997.9 m
  chirp resolution = 30.0 m
```

**What this cell does — Same numbers from the helpers.**

The replication pass. The same samples, sweep, and resolutions now come from the helper package: 400 samples per pulse, sweep to 4.98 MHz, pulse resolution 2997.9 m, chirp resolution 30.0 m. Identical results, packaged for reuse.

From here on, later notebooks call these helpers instead of rebuilding the waveform. Seeing the construction once is enough.

## Matched-filter compression preview

Pulse compression is what turns the long chirp into a sharp peak. The matched filter correlates the received signal with a copy of the transmit waveform. We preview it here with both the plain pulse and the chirp so the difference is visible: the plain pulse's output stays wide, while the chirp collapses to a narrow compressed peak.

Why does the chirp compress and the plain pulse not? The matched filter slides the template across the received signal and adds up the products at each lag. The plain pulse is a flat block with no internal structure, so any overlap looks the same and its output stays wide. The chirp, by contrast, *labels every instant with a unique frequency* as it sweeps across the bandwidth. The products only add constructively at the exact lag where the template's frequency matches the echo's frequency at every instant; slide it a little and the frequency labels no longer line up, so the products cancel and the sum collapses. The wider the bandwidth, the faster that alignment is lost and the narrower the peak — which is why bandwidth, not pulse length, sets the compressed width.

### Notebook cell 24 · code
```python
# Preview the matched-filter output for both waveforms.
from beginner.helpers import matched_filter

mf_rect = matched_filter(rect_pulse, rect_pulse)
mf_chirp = matched_filter(chirp, chirp)

# Zoom in around the peak so the width difference is clear.
peak = np.argmax(np.abs(mf_chirp))
span = pulse_samples
lo, hi = max(0, peak - span), min(len(mf_chirp), peak + span)
idx = np.arange(lo, hi)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(idx, np.abs(mf_rect[lo:hi]) / np.max(np.abs(mf_rect)), color="#d95f02", label="Rectangular pulse")
ax.plot(idx, np.abs(mf_chirp[lo:hi]) / np.max(np.abs(mf_chirp)), color="#1b9e77", label="LFM chirp")
ax.set_xlabel("Sample index around the compressed peak")
ax.set_ylabel("Normalized magnitude")
ax.set_title("Matched-filter output: chirp compresses, plain pulse stays wide")
ax.legend(loc="upper right")
plt.tight_layout()
plt.show()

print("The chirp peak is narrow because its bandwidth, not its length, sets the width.")
print("Notebook 03 will turn this peak delay into a range estimate.")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
The chirp peak is narrow because its bandwidth, not its length, sets the width.
Notebook 03 will turn this peak delay into a range estimate.
```

![Notebook output](assets/01/fig_cell24_0.png)

**What this cell does — Pulse-compression preview.**

The matched filter slides a copy of the transmit waveform across the received signal and sums the product at each lag. The plain pulse's output stays wide, because a flat block matches equally well at every overlap. The chirp collapses to a narrow peak, because its frequency labels align at only one precise lag.

The chirp peak is only a few samples wide while the plain pulse stays roughly 400 wide: the bandwidth, not the pulse length, sets the width. The final printed line tells you where this is headed - Notebook 03 turns this peak's delay into a range estimate.

## Closing the loop: answers to the opening questions

At the start of this notebook we listed four things you should be able to explain. Here is a direct answer to each one, using the physics, equations, and numbers we just worked through.

### What a rectangular pulse looks like in time

A rectangular pulse is simply the transmitter on at full amplitude for the pulse width, then off. In sampled form it is a block of ones, and its length is $N = f_s \cdot \tau$. With the baseline values that is $N = 20\ \text{MHz} \times 20\ \mu\text{s} = 400$ samples. There is no sweep, no hidden structure — just a flat burst of energy whose frequency content is limited to roughly $1/\tau = 50$ kHz. You saw this built directly in the first code cell and plotted as the top trace in the side-by-side figure.

### What an LFM chirp is and how its frequency sweeps

An LFM chirp keeps the same 400 samples and the same amplitude, but the complex phase now rises quadratically. The waveform is $s(t) = \exp\!\left(j \pi \frac{B}{\tau} t^{2}\right)$, with chirp rate $B/\tau = 2.5 \times 10^{11}$ Hz/s. The instantaneous frequency, visible in the second plot, ramps linearly from near zero up to approximately 5 MHz — the bandwidth — across the 20-microsecond pulse. That is the whole difference from the plain pulse: the frequency sweeps, and the sweep covers a band far wider than $1/\tau$. Everything that follows in this notebook hangs on that single fact.

### Why a chirp resolves targets much closer together than its pulse length suggests

Range resolution for a plain pulse is $\Delta R = c\tau/2 = 2997.9$ m. For a chirp after pulse compression it is $\Delta R = c/(2B) = 30.0$ m — a 100x improvement. The reason is visible in the matched-filter plot: the plain-pulse output stays wide, roughly 400 samples across, while the chirp collapses to a peak only a few samples wide. The compressed width is set by $1/B$, not by $\tau$. Because the bandwidth can be made far larger than the inverse pulse length, the chirp decouples energy from resolution — the pulse stays long for energy, the bandwidth stays wide for sharpness. The 100x factor you saw in the resolution comparison cell is the direct arithmetic of that decoupling.

### What the time-bandwidth product tells you about that advantage

The time-bandwidth product is $TBP = B \cdot \tau = 5\ \text{MHz} \times 20\ \mu\text{s} = 100$. That number is the compression ratio: the long chirp, squeezed by the matched filter, produces a peak roughly 100 times narrower than the pulse itself. It measures exactly how much work the chirp is doing compared to a plain pulse of the same length. A large time-bandwidth product is what makes modern pulse radar practical — it lets the system stay loud and still resolve closely spaced targets. The TBP you computed in the cell above is the single number that captures the entire trade.

If you can retell these four answers in your own words — what the plain pulse is, how the chirp sweeps, why the bandwidth buys resolution, and what the time-bandwidth product means — you have the message of this notebook.

## Summary

In this notebook you went inside the transmit burst and built two waveforms. The rectangular pulse is simply on for the pulse width; its resolution is tied directly to that length. The LFM chirp keeps the same length but sweeps frequency across the bandwidth, and that sweep is what gives pulse compression its power.

The two formulas tell the story: $\Delta R = c\tau/2$ for the plain pulse, but $\Delta R = c/(2B)$ once the chirp is compressed. Because the bandwidth can be far larger than the inverse pulse length, a long, energetic chirp still resolves closely spaced targets. The time-bandwidth product captures exactly how much compression the waveform achieves.

The main takeaway is that radar resolution is a bandwidth story, not just a pulse-length story. The matched-filter preview at the end shows the practical result: the long chirp collapses into a sharp peak, which is the object Notebook 03 will later convert into range. For now, you should remember that the chirp lets the radar be both loud and sharp at the same time.
