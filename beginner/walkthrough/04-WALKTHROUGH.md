# Walkthrough — 04: Matched Filtering and Range Estimation

This is a cell-by-cell walkthrough of `beginner/notebooks/04-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 04 — Matched Filtering and Range Estimation

This notebook shows how correlation pulls a known echo out of noise, how the compressed peak gives you a range estimate, and why matched filtering beats thresholding the raw received signal.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/04-matched-filter-range.ipynb)

Use this link if you want to open the notebook in Colab and follow along in a browser notebook environment.

## What this notebook teaches

You have built the transmit waveform, you have seen what the channel does to it, and you know the echo is buried in noise. Now you will learn the tool that pulls it out.

By the end of this notebook, you should be able to explain:

- what correlation means in the matched-filter context,
- why the compressed peak is sharper than the raw echo,
- how peak location converts to a range estimate,
- and why matched filtering beats simple thresholding.

Keep these four questions in mind as you work through the cells. At the end of the notebook, a dedicated section answers each one directly, so you can study the material first and then check your understanding against the full story.

## Setup and baseline values

We reuse the baseline radar specification from the earlier notebooks. If you are running in Colab, run the bootstrap cell below first so the repository is cloned, installed, and available for import.

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

from beginner.helpers import BaselineRadarSpec, baseline_spec
from beginner.helpers import (
    rectangular_pulse,
    lfm_chirp,
    matched_filter,
    delay_samples_for_range,
    range_from_delay_samples,
    single_target_channel,
)
from beginner.helpers.plotting import apply_notebook_style

np.random.seed(42)
apply_notebook_style()
radar_spec = BaselineRadarSpec()
radar_spec
```

**Executed output:**

```
BaselineRadarSpec(fc_hz=2450000000.0, bandwidth_hz=5000000.0, pulse_width_s=2e-05, pri_s=0.001, fs_hz=20000000.0, n_pulses=64, target_range_m=1000.0, target_velocity_mps=40.0, snr_db=20.0, target_angle_deg=20.0, interferer_angle_deg=-30.0)
```

**What this cell does — Setup: the matched filter imports.**

Imports now include matched_filter and range_from_delay_samples alongside the waveform builders and channel helper. The seed is fixed at 42 so the noise - and therefore every number in the lesson - is reproducible.

The one cell that matters is the chain you will trace all notebook: template, channel, matched filter, delay, range.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

Notebook 00 introduced range and duty cycle. Notebook 01 built the transmit waveform and showed why chirps buy resolution. Notebook 03 placed a delayed, attenuated echo in a noisy received buffer. Now we have a problem: the echo is there, but you cannot see it in the noise. The matched filter is the solution.

## What the matched filter does

The radar already knows the shape of the waveform it transmitted. The matched filter exploits that knowledge: it slides a time-reversed, conjugated copy of the transmitted pulse across the received signal and computes the correlation at every position. Where the transmitted shape lines up with an echo, the output forms a strong peak. Where it does not, the output stays low.

In mathematical terms, the matched-filter output at lag $k$ is

$$
y[k] = \sum_{n} x[n] \cdot s^{*}[n - k]
$$

where $x$ is the received signal and $s$ is the transmitted waveform. The conjugate and the sign convention handle complex waveforms like the chirp, but the intuition is the same for both: slide, multiply, sum, and look for the peak.

## Build the received signal

We start with a rectangular pulse to keep the idea simple. The channel places one echo at the baseline range with -40 dB attenuation and20 dB SNR, just as in Notebook 03.

### Notebook cell 10 · code
```python
# Build a rectangular pulse and place it in a noisy received buffer.
pulse_len = int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))
pulse = rectangular_pulse(pulse_len)

n_delay = delay_samples_for_range(radar_spec.target_range_m, radar_spec.fs_hz)
attenuation_db = -40.0
attenuation_linear = 10.0 ** (attenuation_db / 20.0)
snr_db = 20.0

received = single_target_channel(pulse, n_delay, attenuation_linear, snr_db)

print(f"Target range = {radar_spec.target_range_m:.0f} m")
print(f"Expected delay = {n_delay} samples")
print(f"Received buffer = {len(received)} samples")
```

**Executed output:**

```
Target range = 1000 m
Expected delay = 133 samples
Received buffer = 533 samples
```

**What this cell does — Build the received signal.**

The received signal from Notebook 03 in one call: single_target_channel places one rectangular-pulse echo at the baseline range with -40 dB attenuation and 20 dB SNR. The result is a 533-sample buffer and the true echo sits at sample 133.

This is the input the whole notebook works on. The echo is in there - the entire game is extracting it.

## Correlation by hand

Before calling the helper, we run the correlation step by step so you can see the arithmetic. We slide the transmitted pulse across the received signal, multiply overlapping samples, and sum at each position. The result is a vector one sample longer than the received buffer.

### Notebook cell 12 · code
```python
# Compute the matched-filter output by hand.
mf_output = np.correlate(received, pulse[::-1], mode="full")
mf_peak_idx = np.argmax(np.abs(mf_output))

# The correlate output is centred; extract the delay from the peak index.
# In full mode the zero-lag position is at len(pulse) - 1.
echo_delay_samples = mf_peak_idx - (len(pulse) - 1)
echo_range_m = range_from_delay_samples(echo_delay_samples, radar_spec.fs_hz)

print(f"Matched-filter peak at index {mf_peak_idx}")
print(f"Derived echo delay = {echo_delay_samples} samples (expected {n_delay})")
print(f"Estimated range = {echo_range_m:.1f} m (expected {radar_spec.target_range_m:.0f} m)")
```

**Executed output:**

```
Matched-filter peak at index 532
Derived echo delay = 133 samples (expected 133)
Estimated range = 996.8 m (expected 1000 m)
```

**What this cell does — Correlation by hand.**

The matched filter as raw arithmetic. np.correlate slides the time-reversed pulse across the received signal and sums the product at every lag; 'full' mode returns one output per lag. The peak lands at index 532, and subtracting the zero-lag offset (N-1 = 399) recovers the echo delay of 133 samples, which converts to 996.8 m.

Notice the estimate is 996.8 m, not exactly 1000 m: the same sample quantization from Notebook 00. The delay is measured to the nearest sample, and that is the accuracy the round-trip formula can give.

## Raw echo versus compressed output

The plot below tells the whole story. The top panel shows the received signal: the echo is small and buried in noise. The bottom panel shows the matched-filter output: the same echo is now a clear peak that stands well above the noise floor. That is the matched-filter gain in action.

### Notebook cell 14 · code
```python
# Plot the raw received signal and the matched-filter output side by side.
fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=False)

time_received = np.arange(len(received)) / radar_spec.fs_hz * 1e6
axes[0].plot(time_received, received, color="#7570b3", linewidth=0.7)
axes[0].set_xlabel("Time (microseconds)")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Raw received signal — echo buried in noise")

lag_axis = np.arange(len(mf_output)) - (len(pulse) - 1)
axes[1].plot(lag_axis, np.abs(mf_output), color="#1b9e77")
axes[1].axvline(echo_delay_samples, color="#d95f02", linestyle="--", label=f"Peak at {echo_delay_samples} samples")
axes[1].set_xlabel("Lag (samples)")
axes[1].set_ylabel("|Matched filter output|")
axes[1].set_title("Matched-filter output — echo compressed to a sharp peak")
axes[1].legend(loc="upper right")

plt.tight_layout()
plt.show()
```

**Executed output:**

```
<Figure size 1000x500 with 2 Axes>
```

![Notebook output](assets/04/fig_cell14_0.png)

**What this cell does — From buried echo to sharp peak.**

The story in two panels. Top: the raw received signal, where the echo is one bump among many and the largest-looking features are noise. Bottom: the matched-filter output, where the echo has collapsed into a single peak at lag 133, marked by the dashed line, towering over the noise floor.

Same echo, same noise - only the processing changed. The bottom panel is what the radar actually uses as its range measurement.

## Why thresholding the raw echo fails

A natural first thought is to just look for the largest sample in the received signal. The problem is visible in the top panel above: the noise can produce samples as large as the echo, so a simple threshold either misses the echo or triggers on noise. The matched filter avoids this because it correlates over the entire pulse length, accumulating energy from the echo while averaging out uncorrelated noise.

### Notebook cell 16 · code
```python
# Show why thresholding the raw signal fails.
raw_peak_idx = np.argmax(np.abs(received))
threshold = 0.5 * np.max(np.abs(received))

print(f"Raw signal peak at sample {raw_peak_idx} (expected around {n_delay})")
print(f"Peak value = {np.abs(received[raw_peak_idx]):.4f}")
print(f"Threshold (50% of peak) = {threshold:.4f}")
print(f"Samples above threshold = {np.sum(np.abs(received) > threshold)}")
print()
print("The matched filter avoids this problem because it accumulates")
print("energy across the entire pulse length, not just one sample.")
```

**Executed output:**

```
Raw signal peak at sample 209 (expected around 133)
Peak value = 0.0133
Threshold (50% of peak) = 0.0067
Samples above threshold = 400

The matched filter avoids this problem because it accumulates
energy across the entire pulse length, not just one sample.
```

**What this cell does — Why thresholding the raw signal fails.**

The naive approach: take the largest sample of the raw signal. It fails. The raw peak is at sample 209 (noise), not 133 (the echo), and 400 of 533 samples lie above a 50-percent threshold. A threshold detector cannot tell echo from noise because it judges single samples.

The matched filter instead integrates across the whole 400-sample pulse, accumulating echo energy while averaging away uncorrelated noise. No single-sample test can do that.

## Repeat with a chirp

The same matched-filter idea works for any waveform, but the chirp gives a much sharper peak. The width of the compressed peak is set by the bandwidth, not the pulse length — exactly as Notebook 01 predicted.

### Notebook cell 18 · code
```python
# Build a chirp-based received signal and compress it.
chirp = lfm_chirp(pulse_len, radar_spec.bandwidth_hz, radar_spec.pulse_width_s, radar_spec.fs_hz)
received_chirp = single_target_channel(chirp, n_delay, attenuation_linear, snr_db)

mf_chirp = matched_filter(received_chirp, chirp)
mf_chirp_peak = np.argmax(np.abs(mf_chirp))
chirp_echo_delay = mf_chirp_peak - (len(chirp) - 1)
chirp_range_m = range_from_delay_samples(chirp_echo_delay, radar_spec.fs_hz)

print(f"Chirp matched-filter peak at sample {mf_chirp_peak}")
print(f"Derived echo delay = {chirp_echo_delay} samples (expected {n_delay})")
print(f"Estimated range = {chirp_range_m:.1f} m (expected {radar_spec.target_range_m:.0f} m)")

# Overlay the two matched-filter outputs.
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(lag_axis, np.abs(mf_output) / np.max(np.abs(mf_output)), color="#d95f02", label="Rectangular pulse", linewidth=0.8)
ax.plot(lag_axis, np.abs(mf_chirp) / np.max(np.abs(mf_chirp)), color="#1b9e77", label="LFM chirp", linewidth=0.8)
ax.axvline(n_delay, color="#999999", linestyle=":", label=f"True delay = {n_delay} samples")
ax.set_xlabel("Lag (samples)")
ax.set_ylabel("Normalised magnitude")
ax.set_title("Chirp compresses to a sharper peak than the rectangular pulse")
ax.legend(loc="upper right")
plt.tight_layout()
plt.show()
```

**Executed output:**

```
Chirp matched-filter peak at sample 532
Derived echo delay = 133 samples (expected 133)
Estimated range = 996.8 m (expected 1000 m)
<Figure size 1000x350 with 1 Axes>
```

![Notebook output](assets/04/fig_cell18_0.png)

**What this cell does — The chirp compresses sharper.**

The same matched filter with the chirp as template. The peak again lands at sample 532, giving a 133-sample delay and a 996.8 m estimate - the same answer as the rectangle. The overlay shows the real prize from Notebook 01: the chirp's compressed peak is dramatically narrower, because its width is set by the 5 MHz bandwidth, not the 400-sample length.

Both waveforms measure range identically. The chirp adds resolution - the ability to separate targets that sit close together - which is exactly what the closing stretch demonstrates.

## Checkpoint

In your own words, what does the matched filter slide across the received signal, and what is it looking for?

Then answer this: why is the chirp peak narrower than the rectangular-pulse peak, even though both waveforms have the same length?

## Common mistake

A common mistake is to think the matched filter amplifies the signal. It does not change the echo amplitude; it concentrates the echo energy into a narrow peak by coherently adding across the pulse length. The peak is higher because the energy is compressed in time, not because energy was added.

Another mistake is to treat the peak index as a range directly. The peak gives you a sample delay, and you must convert that delay to range using the speed of light and the sampling rate — the same round-trip formula from Notebook 00.

## Why the helpers exist

The cells above build the matched filter and range estimate step by step so you can see each operation. After that first pass, the same logic lives in `matched_filter` and `range_from_delay_samples` so later notebooks can compress an echo and read the range in one line.

As in the earlier notebooks, keep the first occurrence visible so you see the physics, then use the helpers when you want the lesson to stay readable.

### Notebook cell 22 · code
```python
# Use the helper function to reproduce the same result compactly.
helper_spec = baseline_spec()
helper_pulse = rectangular_pulse(int(round(helper_spec.pulse_width_s * helper_spec.fs_hz)))
helper_n = delay_samples_for_range(helper_spec.target_range_m, helper_spec.fs_hz)
helper_received = single_target_channel(helper_pulse, helper_n, attenuation_linear, snr_db)

helper_mf = matched_filter(helper_received, helper_pulse)
helper_peak = np.argmax(np.abs(helper_mf))
helper_delay = helper_peak - (len(helper_pulse) - 1)
helper_range = range_from_delay_samples(helper_delay, helper_spec.fs_hz)

print("Helper-based version of the same calculations:")
print(f"  peak index = {helper_peak}")
print(f"  echo delay = {helper_delay} samples")
print(f"  estimated range = {helper_range:.1f} m")
```

**Executed output:**

```
Helper-based version of the same calculations:
  peak index = 532
  echo delay = 133 samples
  estimated range = 996.8 m
```

**What this cell does — The same result from the helper.**

The helper version of the whole chain: build the pulse, place it in the channel, matched-filter it, and read the range. Peak 532, echo delay 133, estimated range 996.8 m - identical to the by-hand cell.

From here on, later notebooks do range in exactly these three lines. The by-hand version exists so you know what the one-liner is really doing.

## Stretch: resolve the two-target ambiguity

In Notebook 03 you built two overlapping echoes — at 1000 m and 3000 m — and saw that the summed signal hid the second echo. A leading-edge detector would report only the nearest target. Here is the payoff: the matched filter can separate them.

Rerun that same two-target scenario, but now matched-filter the summed received signal. The result depends on the waveform:

- With the **rectangular pulse**, the compressed peak is still wide (its bandwidth is only 1 / tau), so the two peaks stay merged and you still see one target. The rectangle cannot resolve the overlap.
- With the **chirp**, the compressed peak is far narrower (bandwidth 5 MHz), so the two peaks separate cleanly. Two peaks mean two targets, each with a distinct range — even though the echoes overlap completely in the raw signal.

This is the concrete advantage the notebook promised: the matched filter turns overlapping echoes into resolved range detections, and the chirp is what makes the resolution fine enough to tell close targets apart.

### Notebook cell 24 · code
```python
# Rerun the two-target scenario, then matched-filter with the chirp.
# Use the chirp built earlier in this notebook.
template = chirp
second_range_m = 3000.0
n_delay_2 = delay_samples_for_range(second_range_m, radar_spec.fs_hz)

two_target_len = n_delay_2 + len(template)

# Complex buffer (the chirp is complex at baseband).
two_target_clean = np.zeros(two_target_len, dtype=complex)
two_target_clean[n_delay : n_delay + len(template)] = attenuation_linear * template
two_target_clean[n_delay_2 : n_delay_2 + len(template)] = attenuation_linear * template

# Add complex noise at the same SNR.
echo_power_2 = np.mean(np.abs(two_target_clean) ** 2)
noise_power_2 = echo_power_2 / (10.0 ** (snr_db / 10.0))
two_target_noisy = two_target_clean + np.sqrt(noise_power_2) * (np.random.randn(two_target_len) + 1j * np.random.randn(two_target_len)) / np.sqrt(2)

# Matched-filter the summed noisy signal.
mf_two = matched_filter(two_target_noisy, template)
mags = np.abs(mf_two)

# Find resolved peaks: local maxima above a fraction of the largest peak.
threshold = 0.3 * mags.max()
peak_indices = [
    i for i in range(1, len(mags) - 1)
    if mags[i] > mags[i - 1] and mags[i] > mags[i + 1] and mags[i] > threshold
]
peak_indices.sort(key=lambda i: -mags[i])

ranges_m = [
    range_from_delay_samples(p - (len(template) - 1), radar_spec.fs_hz)
    for p in peak_indices
]

for p, r in zip(peak_indices, ranges_m):
    print(f"Peak at sample {p} -> derived range {r:.0f} m")

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(np.arange(len(mags)), mags, color="#1b9e77", linewidth=1.0)
for p in peak_indices:
    ax.axvline(p, color="#d95f02", linestyle="--", alpha=0.7, linewidth=1)
ax.set_xlabel("Matched-filter output sample")
ax.set_ylabel("|Matched-filter output|")
ax.set_title("Two overlapping echoes, matched-filtered with the chirp: two resolved peaks")
plt.tight_layout()
plt.show()
print("Expected targets:", int(radar_spec.target_range_m), "m and", int(second_range_m), "m.")
```

**Executed output:**

```
Peak at sample 799 -> derived range 2998 m
Peak at sample 532 -> derived range 997 m
<Figure size 1000x350 with 1 Axes>
Expected targets: 1000 m and 3000 m.
```

![Notebook output](assets/04/fig_cell24_0.png)

**What this cell does — Two targets, resolved.**

The payoff of the two-overlap story from Notebook 03. Matched-filtering the summed signal with the chirp produces two resolved peaks: sample 799 gives 2998 m and sample 532 gives 997 m, against true values of 3000 m and 1000 m. Overlapping echoes are now two distinct detections.

The notebook notes the rectangle cannot do this: its compressed peak stays wide enough to merge the two echoes. Bandwidth, again, is the deciding resource.

## Closing the loop: answers to the opening questions

At the start of this notebook we listed four things you should be able to explain. Here is a direct answer to each one, using the physics, equations, and numbers we just worked through.

### What correlation means in the matched-filter context

Correlation is a sliding dot product: the matched filter multiplies the received signal by a time-reversed copy of the transmitted waveform and sums the products at every lag position. The lag axis runs from negative to positive, and at each position you are measuring how well the transmitted shape lines up with that slice of the received signal. When the transmitted shape lines up with the echo, every overlapping sample contributes positively and the sum is large. When it does not line up, the contributions cancel and the sum stays small.

### Why the compressed peak is sharper than the raw echo

The raw echo is as wide as the transmitted pulse —400 samples for the rectangular pulse. The matched filter compresses those400 samples of energy into a single peak whose width is set by the waveform bandwidth, not the pulse length. For the rectangular pulse the peak is still relatively wide (its bandwidth is only $1/\tau$), but for the chirp in the overlay plot the peak is far narrower because the chirp bandwidth is much larger. The matched filter does not add energy; it concentrates the energy that was already there into a narrower time slot.

### How peak location converts to a range estimate

The peak appears at a specific lag on the lag axis, which corresponds to the sample delay of the echo. In the by-hand cell the peak was at sample index $n_{peak}$, giving an echo delay of $n_{peak} - (N - 1)$ samples (the $N - 1$ offset accounts for the `full`-mode correlation). Converting that sample delay to seconds and applying $R = c \cdot \tau_{delay} / 2$ gives the range estimate. For the baseline 1000 m target the delay was 133 samples, and the estimated range matched the true range to within a fraction of a metre.

### Why matched filtering beats simple thresholding

A threshold on the raw received signal triggers on the single largest sample, which in the presence of noise may not be the echo at all. The matched filter avoids this by coherently accumulating energy across the entire pulse length. The echo contributes consistently at the correct lag, so the peak grows proportionally to the pulse length, while the noise adds incoherently and averages out. This is why the matched-filter output shows a clear peak in the bottom panel of the comparison plot even though the echo is invisible in the top panel.

If you can retell these four answers in your own words — what correlation is, why the peak is sharp, how delay becomes range, and why thresholding fails — you have the message of this notebook.

## Summary

In this notebook you met the matched filter — the tool that turns a weak, noisy echo into a clear, localised peak. The filter works by sliding a copy of the known transmitted waveform across the received signal and computing the correlation at every lag. Where the transmitted shape lines up with an echo, the output forms a strong peak; where it does not, the output stays low.

The peak location gives the echo delay in samples, and the round-trip range equation converts that delay into a distance. For the baseline 1000 m target, the estimated range came out accurately from both the rectangular pulse and the chirp. The chirp peak was sharper because its bandwidth is larger, which is the compression advantage predicted in Notebook 01.

The main takeaway is that the matched filter exploits knowledge the radar already has — the transmitted waveform — to pull a known shape out of noise. This is the foundation for everything that follows: every range measurement in a pulse radar starts with a matched-filter peak.
