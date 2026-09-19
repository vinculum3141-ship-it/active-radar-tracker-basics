# Walkthrough — 10: Integration and Portfolio Artifacts

This is a cell-by-cell walkthrough of `beginner/notebooks/10-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 10 — Integration and Portfolio Artifacts

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/10-integration-artifacts.ipynb)

## What this notebook teaches

This is the closing notebook. It does not introduce new physics - instead it joins the pieces you have built one at a time into one coherent pipeline, from the transmitted waveform all the way to steering and adaptive nulling, and gathers the results into a single *portfolio artifact*. It is your chance to see the whole radar digital signal-processing chain on one page, and to be able to describe it end to end.

By the end of this notebook, you should be able to explain:

- how the range-Doppler map and the beam-nulling results fit in one pipeline,
- where each earlier notebook contributes to the whole system,
- how the pieces share one baseline scene and set of helpers,
- how the final artifacts are produced and exported,
- and how to tell the entire radar story in your own words.

Keep these five questions in mind as you work through the cells. A dedicated section at the end answers each one directly.

## Setup and baseline values

The demonstrations share a baseline specification: a 2.45 GHz carrier, 5 MHz bandwidth, 20 microsecond chirp, 1 ms PRI, 20 MHz sampling, 64 pulses, and a target at 1000 m. This notebook reuses the relevant helper modules from earlier lessons. Its panels are linked demonstrations using common parameters, rather than one simulated data cube passed through every stage.

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

The same door as every notebook in this course. In Colab this cell clones the repository, installs the beginner package, and steps into the workspace. Running locally it locates the repo root, puts it on the import path, and prints where you are working.

Run this cell once. Every following cell expects it to have run.

### Notebook cell 5 · code
```python
import numpy as np
import matplotlib.pyplot as plt

from beginner.helpers import baseline_spec
from beginner.helpers.math import wavelength_m, delay_samples_for_range, range_from_delay_samples, range_resolution_from_bandwidth
from beginner.helpers.waveforms import lfm_chirp, matched_filter
from beginner.helpers.doppler import build_pulse_stack, range_doppler_map, doppler_frequency_hz
from beginner.helpers.array import array_factor, steering_vector
from beginner.helpers.steering import steering_weights, lcmv_weights
from beginner.helpers.doa import sample_covariance, bartlett_spectrum, mvdr_spectrum
from beginner.helpers.plotting import apply_notebook_style

np.random.seed(42)
apply_notebook_style()
radar_spec = baseline_spec()

lam = wavelength_m(radar_spec.fc_hz)
fs = radar_spec.fs_hz
n_elements = 8
d_spacing = lam / 2.0
angles = np.linspace(-90, 90, 1801)

print(f"Carrier {radar_spec.fc_hz/1e9:.2f} GHz, lambda = {lam*100:.2f} cm, B = {radar_spec.bandwidth_hz/1e6:.0f} MHz")
print(f"Target at {radar_spec.target_range_m:.0f} m; range resolution ~ {range_resolution_from_bandwidth(radar_spec.bandwidth_hz):.1f} m")
```

**Executed output:**

```
Carrier 2.45 GHz, lambda = 12.24 cm, B = 5 MHz
Target at 1000 m; range resolution ~ 30.0 m
```

**What this cell does — Setup: the whole toolkit on stage.**

Imports now span the entire chain in one go: waveforms, matched filter, pulse stack, range-Doppler map, array factor, steering vector, steering and LCMV weights, and the DOA scans. The header numbers frame everything: 2.45 GHz carrier, 12.24 cm wavelength, 5 MHz bandwidth, and 30.0 m range resolution.

This closing notebook introduces no new physics - every name here was built by hand in an earlier lesson. The point is that the whole chain now fits in a few readable cells.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## The full chain at a glance

Here is the whole system this track has built, and the notebook that produced each stage:

1. **Waveform** (Notebook 1) - an LFM chirp is transmitted.
2. **Channel** (Notebooks 2-3) - the echo returns later, weaker, and with noise.
3. **Range** (Notebook 4) - the matched filter compresses the echo into a peak at the delay that gives range.
4. **Velocity** (Notebook 5) - the phase drifting across pulses gives the Doppler velocity.
5. **Tracking** (Notebook 6) - a Kalman filter smooths noisy range and velocity across time.
6. **Angle** (Notebooks 7-8) - the array turns time-of-arrival differences into direction.
7. **Interference rejection** (Notebooks 8-9) - DOA finds directions; steering and LCMV null a jammer.

This notebook revisits the chain with linked demonstrations and collects their artifacts. We reuse the helpers so the recap fits in a handful of short cells.

## Shared baseline across the demonstrations

To keep the recap coherent, reuse the same baseline parameters: a target at 1000 m moving at 20 m/s, with target angle +20 degrees and an interferer direction of -30 degrees in the nulling demonstration. The range-Doppler calculation models the moving target; the angle and null plots are separate spatial demonstrations. First build the waveform and the per-pulse echo stack.

Before the final artifact cells, verify the key numbers one more time explicitly. This makes the portfolio summary a coherent recap of the same physical quantities the earlier notebooks explained in detail, instead of a set of disconnected plots.

### Notebook cell 9 · code
```python
# Explicit recap of the key numbers used throughout the course.
carrier_wavelength_m = wavelength_m(radar_spec.fc_hz)
range_delay_s = (2.0 * radar_spec.target_range_m) / 299_792_458.0
delay_samples = delay_samples_for_range(radar_spec.target_range_m, radar_spec.fs_hz)
range_resolution_m = 299_792_458.0 / (2.0 * radar_spec.bandwidth_hz)
doppler_hz = doppler_frequency_hz(20.0, radar_spec.fc_hz)

print(f"carrier wavelength = {carrier_wavelength_m:.4f} m")
print(f"round-trip delay = {range_delay_s*1e6:.2f} microseconds")
print(f"delay samples at fs = {delay_samples} samples")
print(f"range resolution = {range_resolution_m:.2f} m")
print(f"20 m/s Doppler = {doppler_hz:.1f} Hz")
print(f"These are the same numbers reused across the full chain.")
```

**Executed output:**

```
carrier wavelength = 0.1224 m
round-trip delay = 6.67 microseconds
delay samples at fs = 133 samples
range resolution = 29.98 m
20 m/s Doppler = 326.9 Hz
These are the same numbers reused across the full chain.
```

**What this cell does — The recap numbers, one more time.**

The course's key numbers verified in one breath: wavelength 0.1224 m, round-trip delay 6.67 microseconds = 133 samples, range resolution 29.98 m, and 326.9 Hz Doppler for 20 m/s.

These are the same values each earlier notebook derived - the shared baseline keeps every stage consistent.

### Notebook cell 10 · code
```python
pulse_len = int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))
chirp = lfm_chirp(pulse_len, radar_spec.bandwidth_hz, radar_spec.pulse_width_s, radar_spec.fs_hz)

fig, ax = plt.subplots(figsize=(9, 3.5))
t_us = np.arange(len(chirp)) / radar_spec.fs_hz * 1e6
ax.plot(t_us, chirp.real, color="#1b9e77", linewidth=1.5)
ax.set_xlabel("Time (microseconds)")
ax.set_ylabel("Amplitude (I)")
ax.set_title("Artifact 1 - the LFM chirp waveform")
plt.tight_layout()
plt.show()

print(f"Chirp: {pulse_len} samples, {radar_spec.pulse_width_s*1e6:.0f} us long, bandwidth {radar_spec.bandwidth_hz/1e6:.0f} MHz")
print(f"Range resolution: {range_resolution_from_bandwidth(radar_spec.bandwidth_hz):.1f} m (from Notebook 1)")
```

**Executed output:**

```
<Figure size 900x350 with 1 Axes>
Chirp: 400 samples, 20 us long, bandwidth 5 MHz
Range resolution: 30.0 m (from Notebook 1)
```

![Notebook output](assets/10/fig_cell10_0.png)

**What this cell does — Artifact 1: the chirp.**

The first portfolio panel: the 400-sample, 20-microsecond, 5 MHz LFM chirp - the waveform every later stage processes.

From it, range resolution is already fixed at 30.0 m by the bandwidth.

## Artifact: range from matching

Feed the echo into the matched filter. The chirp compresses into a sharp peak whose position is the two-way delay to the target, converted to range in Notebook 4.

### Notebook cell 12 · code
```python
n_delay = delay_samples_for_range(radar_spec.target_range_m, radar_spec.fs_hz)
echo = np.zeros(n_delay + len(chirp), dtype=complex)
echo[n_delay:n_delay + len(chirp)] += chirp
matched = matched_filter(echo, chirp)
range_axis_mf = range_from_delay_samples(np.arange(len(matched)) - (pulse_len - 1), radar_spec.fs_hz)

fig, ax = plt.subplots(figsize=(9, 3.5))
ax.plot(range_axis_mf, np.abs(matched), color="#d95f02", linewidth=1.5)
ax.set_xlabel("Range (m)")
ax.set_ylabel("Matched-filter output")
ax.set_title("Artifact 2 - the echo compressed to a range peak")
ax.set_xlim(500, 1500)
plt.tight_layout()
plt.show()

peak_r = range_axis_mf[np.argmax(np.abs(matched))]
print(f"Matched-filter peak at {peak_r:.0f} m (true 1000 m) - range measurement (Notebook 4)")
```

**Executed output:**

```
<Figure size 900x350 with 1 Axes>
Matched-filter peak at 997 m (true 1000 m) - range measurement (Notebook 4)
```

![Notebook output](assets/10/fig_cell12_0.png)

**What this cell does — Artifact 2: range from matching.**

One clean echo through the matched filter: the compressed peak sits at 997 m against the true 1000 m - the delay-to-range measurement from Notebook 4.

One metre of difference is sample quantization (133 samples at 20 MHz lands the grid at 996.8 m), and the range axis here rounds to the nearest metre.

## Artifact: range-Doppler map

Now repeat over the 64 pulses with a moving target. The slow-time FFT turns the echo's phase drift into a velocity axis, giving the range-Doppler map of Notebook 5 - range down one axis, velocity across the other.

### Notebook cell 14 · code
```python
v_target = 20.0
fd = doppler_frequency_hz(v_target, radar_spec.fc_hz)
stack = build_pulse_stack(chirp, radar_spec.n_pulses, radar_spec.pri_s, fd, n_delay, amplitude=1.0)
profiles = np.array([matched_filter(stack[k], chirp) for k in range(radar_spec.n_pulses)])
_, velocity_axis, rdm = range_doppler_map(profiles, radar_spec.pri_s, radar_spec.fc_hz)
range_axis = range_from_delay_samples(np.arange(profiles.shape[1]) - (pulse_len - 1), radar_spec.fs_hz)

fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(rdm, aspect="auto", origin="lower",
               extent=[range_axis[0], range_axis[-1], velocity_axis[0], velocity_axis[-1]], cmap="viridis")
ax.axhline(0, color="white", linewidth=0.6, linestyle=":")
ax.set_xlim(500, 1500)
ax.set_ylim(-30, 30)
ax.set_xlabel("Range (m)")
ax.set_ylabel("Velocity (m/s)")
ax.set_title("Artifact 3 - range-Doppler map (Notebook 5)")
plt.colorbar(im, ax=ax, label="Echo magnitude")
plt.tight_layout()
plt.show()

def rd_peak(rdm, vel_axis, vel_mps):
    r = np.argmin(np.abs(range_axis - radar_spec.target_range_m))
    return rdm[np.argmin(np.abs(vel_axis - vel_mps)), r]
print(f"RD bin at (1000 m, {v_target:.0f} m/s) stands out: {rd_peak(rdm, velocity_axis, v_target):.0f}")
print(f"Range and velocity both read from one map (Notebook 5).")
```

**Executed output:**

```
<Figure size 900x500 with 2 Axes>
RD bin at (1000 m, 20 m/s) stands out: 25339
Range and velocity both read from one map (Notebook 5).
```

![Notebook output](assets/10/fig_cell14_0.png)

**What this cell does — Artifact 3: the range-Doppler map.**

The same chirp across 64 pulses with a 20 m/s target: matched-filter each pulse, FFT across slow time, and the map shows one bright bin at exactly (1000 m, +20 m/s), magnitude 25,339.

This single figure carries both coordinates from Notebook 5 - range down one axis, velocity across the other.

## Artifact: the beam and the DOA scan

The matched filter compressed the echo in range. A separate array calculation now adds angle: the array factor shows the main lobe and sidelobes of the 8-element half-wavelength beam (Notebook 7), and a Bartlett covariance scan finds the target's direction of arrival (Notebook 8).

### Notebook cell 16 · code
```python
af = array_factor(np.radians(angles), n_elements, d_spacing, lam, weights=np.ones(n_elements))

R_scene = sample_covariance([np.radians(20.0)], [1.0], n_elements, d_spacing, lam, n_snapshots=2000)
P_bart = bartlett_spectrum(R_scene, np.radians(angles), n_elements, d_spacing, lam)

fig, axes = plt.subplots(1, 2, figsize=(12, 3.5))
axes[0].plot(angles, 10*np.log10((np.abs(af)**2) / (np.abs(af)**2).max()), color="#1b9e77", linewidth=2)
axes[0].set_xlabel("Angle (deg)")
axes[0].set_ylabel("Beam power (dB)")
axes[0].set_title("Artifact 4a - beam pattern (Notebook 7)")
axes[0].set_ylim(-30, 2)
axes[1].plot(angles, 10*np.log10(P_bart / P_bart.max()), color="#7570b3", linewidth=2)
axes[1].axvline(20, color="#d95f02", linestyle=":", label="target 20 deg")
axes[1].set_xlabel("Angle (deg)")
axes[1].set_ylabel("Power (dB)")
axes[1].set_title("Artifact 4b - DOA scan (Notebook 8)")
axes[1].legend()
axes[1].set_ylim(-30, 2)
plt.tight_layout()
plt.show()

print(f"First beam null at {np.degrees(np.arcsin(lam / (n_elements * d_spacing))):.1f} deg (Notebook 7)")
print(f"DOA scan peaks at {angles[np.argmax(P_bart)]:.1f} deg - matches the true 20 deg target (Notebook 8)")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
First beam null at 14.5 deg (Notebook 7)
DOA scan peaks at 20.0 deg - matches the true 20 deg target (Notebook 8)
```

![Notebook output](assets/10/fig_cell16_0.png)

**What this cell does — Artifacts 4a/4b: beam and DOA scan.**

Two spatial panels. Left: the 8-element half-wavelength beam pattern from Notebook 7, first null at 14.5 degrees. Right: a Bartlett covariance scan from Notebook 8, peaking at exactly 20.0 degrees - the target's direction.

The beam shows what the array can hear; the scan actually points at the target.

## Artifact: steering and the adaptive null

Finally, point the beam at the target and force a deep null on the interferer with LCMV weights (Notebook 9). The before/after overlay is the interference-rejection artifact - the target is kept at 0 dB while the interferer's direction is driven tens of decibels down.

### Notebook cell 18 · code
```python
w_steer = steering_weights(np.radians(20.0), n_elements, d_spacing, lam)
C, f, w_lcmv = lcmv_weights(np.radians(20.0), [-np.radians(30.0)], n_elements, d_spacing, lam)

def resp_db(w):
    P = np.array([abs(w.conj() @ steering_vector(np.radians(a), n_elements, d_spacing, lam))**2 for a in angles])
    return 10.0 * np.log10(P / P.max())

res_steer = resp_db(w_steer)
res_lcmv = resp_db(w_lcmv)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, res_steer, color="#1b9e77", linewidth=2, label="steer only")
ax.plot(angles, res_lcmv, color="#7570b3", linewidth=2, label="LCMV null")
ax.axvline(20, color="#d95f02", linestyle=":", label="target +20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Response (dB)")
ax.set_title("Artifact 5 - steering vs LCMV null on the interferer (Notebook 9)")
ax.legend()
ax.set_ylim(-40, 2)
plt.tight_layout()
plt.show()

print(f"Steer-only response at -30 deg: {res_steer[np.argmin(np.abs(angles+30))]:.1f} dB")
print(f"LCMV null at -30 deg         : {res_lcmv[np.argmin(np.abs(angles+30))]:.1f} dB")
print(f"Target held at                : {res_lcmv[np.argmin(np.abs(angles-20))]:.1f} dB")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Steer-only response at -30 deg: -18.6 dB
LCMV null at -30 deg         : -319.1 dB
Target held at                : -0.0 dB
```

![Notebook output](assets/10/fig_cell18_0.png)

**What this cell does — Artifact 5: the adaptive null.**

The interference-rejection panel from Notebook 9. Steering alone leaves -18.6 dB at -30 degrees; LCMV forces it to -319.1 dB while holding the target at -0.0 dB.

Tens of decibels down on the jammer, full response on the target - the entire point of constrained weights.

## The portfolio artifact

Gather four results onto one figure: the waveform, the range-Doppler map, the beam-null overlay, and the direction-of-arrival scan. This portfolio image summarizes the chain's main ideas. The panels share baseline parameters, but they are separate demonstrations rather than outputs of one end-to-end simulation.

### Notebook cell 20 · code
```python
fig = plt.figure(figsize=(12, 8))

ax1 = fig.add_subplot(2, 2, 1)
t_us = np.arange(len(chirp)) / radar_spec.fs_hz * 1e6
ax1.plot(t_us, chirp.real, color="#1b9e77", linewidth=1.5)
ax1.set_title("1. Waveform (chirp)")
ax1.set_xlabel("Time (us)")
ax1.set_ylabel("I")

ax2 = fig.add_subplot(2, 2, 2)
im = ax2.imshow(rdm, aspect="auto", origin="lower",
                extent=[range_axis[0], range_axis[-1], velocity_axis[0], velocity_axis[-1]], cmap="viridis")
ax2.set_title("2. Range-Doppler map")
ax2.set_xlabel("Range (m)")
ax2.set_ylabel("Velocity (m/s)")
ax2.set_xlim(500, 1500)
ax2.set_ylim(-30, 30)

ax3 = fig.add_subplot(2, 2, 3)
ax3.plot(angles, res_steer, color="#1b9e77", linewidth=2, label="steer only")
ax3.plot(angles, res_lcmv, color="#7570b3", linewidth=2, label="LCMV null")
ax3.axvline(20, color="#d95f02", linestyle=":")
ax3.axvline(-30, color="#7570b3", linestyle=":")
ax3.set_title("3. Beam and null")
ax3.set_xlabel("Angle (deg)")
ax3.set_ylabel("dB")
ax3.set_ylim(-40, 2)
ax3.legend(fontsize=8)

ax4 = fig.add_subplot(2, 2, 4)
ax4.plot(angles, 10*np.log10(P_bart / P_bart.max()), color="#7570b3", linewidth=2)
ax4.axvline(20, color="#d95f02", linestyle=":")
ax4.set_title("4. DOA scan")
ax4.set_xlabel("Angle (deg)")
ax4.set_ylabel("dB")
ax4.set_ylim(-30, 2)

fig.suptitle("Beginner radar portfolio: waveform -> range-Doppler -> direction -> null", fontsize=12)
plt.tight_layout()
plt.show()

print("Range, velocity, direction, and interference rejection all on one figure.")
```

**Executed output:**

```
<Figure size 1200x800 with 4 Axes>
Range, velocity, direction, and interference rejection all on one figure.
```

![Notebook output](assets/10/fig_cell20_0.png)

**What this cell does — The portfolio figure.**

All four main ideas on one page: waveform, range-Doppler map, beam-and-null overlay, and DOA scan. The figure title says it in one line: waveform -> range-Doppler -> direction -> null.

Not one end-to-end simulation - four linked demonstrations sharing the baseline parameters and helpers.

## Export the artifact

A portfolio artifact earns its keep if it can be saved and shared. Save the composite figure to a PNG file on disk, then confirm it was written - this is the same step the publishing pipeline uses at the end of the track.

### Notebook cell 22 · code
```python
import os
portfolio_path = "radar_portfolio.png"
fig.savefig(portfolio_path, dpi=150, bbox_inches="tight")

print(f"Saved portfolio artifact to {portfolio_path}")
print(f"File size: {os.path.getsize(portfolio_path):,} bytes")
print(f"Exists on disk: {os.path.isfile(portfolio_path)}")
```

**Executed output:**

```
Saved portfolio artifact to radar_portfolio.png
File size: 295,734 bytes
Exists on disk: True
```

**What this cell does — Exporting the artifact.**

The publishing step: save the composite figure as radar_portfolio.png at 150 dpi. The file is 295,734 bytes and confirmed to exist on disk.

This is the same export the publishing pipeline uses - the notebook's artifact is ready to share.

## Where every notebook fits

Put the final story together. The portfolio figure brings earlier stages into one visual summary, with common baseline parameters and reusable helpers:

- **Notebooks 1-2**: waveform and radar equation set the chirp and its power budget.
- **Notebook 3**: the channel places, scales, and adds noise to the echo.
- **Notebook 4**: the matched filter turns delay into range.
- **Notebook 5**: the pulse stack and slow-time FFT add velocity.
- **Notebook 6**: the Kalman filter smooths range and velocity across time.
- **Notebooks 7-8**: the array adds angle, via the beam and DOA scans.
- **Notebook 9**: steering and LCMV add interference (jammer) rejection.
- **Notebook 10 (this one)**: linked demonstrations on one figure.

## Checkpoint

Without looking back at the earlier notebooks, describe the whole chain to yourself: how does a transmitted chirp become a number for (a) range, (b) velocity, and (c) direction - and then how does adaptive nulling keep the target visible in the face of a jammer?

Then list, from memory, which notebook introduced each of: the chirp, the matched filter, the range-Doppler map, the Kalman track, the steering vector, the Capon scan, and the LCMV null.

## Common mistake

A common mistake in an integration notebook is to assume the stages are independent boxes that happen to share a plot. They are not - they share one coherent scene and one set of helpers, and the numbers must stay consistent: the same delay gives the same range whether read by the matched filter or the RD map; the same angle appears in the beam, the DOA scan, and the null. Check that shared consistency rather than trusting each plot in isolation.

Another is to skip the null source. The adaptive null is only as good as the constraint you place on the interferer's direction; if you do not know that direction, you must first *find* it with a DOA scan (Notebook 8). Integration means the stages cooperate, not that each stands alone.

## Why the helpers exist

Every earlier notebook built one piece by hand, then packaged it. This notebook stands on those packages: a waveform helper, channel and Doppler helpers, matched-filter and array helpers, DOA helpers, and steering/null helpers. None of it was magic - you built each from first principles - but the wrappers let the whole pipeline fit in a handful of readable cells, exactly what a real radar signal-processing chain looks like in practice.

## Stretch: rebuild the chain from memory

As a final test, without importing the stage-specific helpers, try to recognise which numbers in the portfolio figure came from *where*. For each of the four panels, state: the notebook that introduced it, one piece of physics it depends on, and one number it reports. This is the last-mile check that the whole track stuck.

### Notebook cell 28 · code
```python
print("Panel-by-panel recap (your own words):")
print("  1. Waveform       -> Notebook 1 ; linear frequency modulation; 20 us chirp, 5 MHz")
print("  2. Range-Doppler  -> Notebook 5 ; Doppler across slow time; target at 1000 m, 20 m/s")
print("  3. Beam & null    -> Notebook 9 ; C^H w = [1, 0]; deep numerical null at -30 deg")
print("  4. DOA scan       -> Notebook 8 ; Bartlett spatial spectrum; peak at 20 deg")
```

**Executed output:**

```
Panel-by-panel recap (your own words):
  1. Waveform       -> Notebook 1 ; linear frequency modulation; 20 us chirp, 5 MHz
  2. Range-Doppler  -> Notebook 5 ; Doppler across slow time; target at 1000 m, 20 m/s
  3. Beam & null    -> Notebook 9 ; C^H w = [1, 0]; deep numerical null at -30 deg
  4. DOA scan       -> Notebook 8 ; Bartlett spatial spectrum; peak at 20 deg
```

**What this cell does — Panel-by-panel recap.**

A printed cheat sheet matching each panel to its notebook: waveform to Notebook 1, range-Doppler to Notebook 5, beam and null to Notebook 9, DOA scan to Notebook 8.

The final checkpoint asks you to reproduce exactly this from memory.

## Closing the loop: answers to the opening questions

At the start we listed five things to be able to explain. Here is each answer.

**How the range-Doppler map and beam-nulling results fit in one pipeline.** The physical processing chain starts with a chirp and echoes, uses a matched filter and slow-time FFT for range and velocity, and uses an array for direction and interference rejection. This notebook demonstrates those stages separately with shared baseline parameters; it does not pass one data cube through all of them.

**Where each earlier notebook contributes.** The chirp (1) is built by the waveform helpers; the echo's delay and selected velocity are staged with the channel and Doppler helpers (3-5); the array and steering/null helpers (7-9) produce the angle and the null. Each stage rests on the helpers its own notebook built.

**How the pieces share parameters and helpers.** The range and velocity calculations use the 1000 m target and the same carrier and pulse repetition interval. The spatial demonstrations use the same array geometry and target angle. Reused helpers make each panel traceable to its earlier lesson.

**How the final artifacts are produced and exported.** Each stage is a short cell that calls the relevant helpers and plots an artifact; the portfolio cell gathers the key panels onto one figure, and a final cell saves that figure to a PNG on disk.

**How to tell the entire radar story in your own words.** Transmit a chirp, receive its delayed, Doppler-shifted, angled echo; compress it to get range, FFT across pulses to get velocity, scan the array to get direction, then steer and null to keep a target visible under a jammer. If you can say that sentence and defend each step, you own the whole chain.

If you can retell these five answers, you have moved from understanding six separate plots to commanding one integrated radar system.

## Summary

In this closing notebook you assembled the beginner radar ideas onto one page. The 1000 m, 20 m/s target drives the range-Doppler example; the same baseline geometry supports separate beam, direction-scan, and constrained-nulling examples. Each stage reuses helpers from earlier lessons. The result is a four-panel portfolio artifact plus a PNG export.

You should now be able to describe the whole story in one breath: a chirp is sent, its echo is compressed for range, processed across pulses for velocity, scanned across an array for direction, and steered and nulled to reject a jammer. The four-panel portfolio figure links these ideas with consistent baseline parameters. A fully integrated data-cube simulation would be a further step beyond this recap.
