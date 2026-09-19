# Walkthrough — 03: Channel Model and Echoes

This is a cell-by-cell walkthrough of `beginner/notebooks/03-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 03 — Channel Model and Echoes

This notebook shows what happens to a pulse after it leaves the antenna: it travels to a target, bounces back, arrives weakened and buried in noise, and lands in the received signal buffer as a delayed echo.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/03-channel-model-echoes.ipynb)

Use this link if you want to open the notebook in Colab and follow along in a browser notebook environment.

## What this notebook teaches

So far you have built the transmit waveform and understood why chirps improve resolution. Now you will see what happens when that waveform travels to a target and comes back.

By the end of this notebook, you should be able to explain:

- how range turns into a sample delay in the received signal,
- what an echo looks like relative to the transmitted pulse,
- why attenuation makes the echo weaker than the original,
- and how noise hides the echo and motivates the matched filter.

Keep these four questions in mind as you work through the cells. At the end of the notebook, a dedicated section answers each one directly, so you can study the material first and then check your understanding against the full story.

## Setup and baseline values

We reuse the baseline radar specification from Notebooks 00 and 01 so every waveform and delay here is built from the same physical case. If you are running in Colab, run the bootstrap cell below first so the repository is cloned, installed, and available for import.

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
    delay_samples_for_range,
    range_from_delay_samples,
    rectangular_pulse,
    lfm_chirp,
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

**What this cell does — Setup: seeds and helpers.**

Imports the delay helpers and waveform builders alongside the baseline spec. Note np.random.seed(42): the noise is random, and fixing the seed makes the noisy plots reproducible - every run of this notebook produces the same echo, the same noise, and the same pictures.

That matters for teaching: the numbers you see here (133 samples, 0.01 amplitude, the shape of the noise) are the same in the lecture, the deck, and on your screen.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

Notebooks 00 and 01 built the transmit side: a rectangular pulse and a chirp, each 400 samples long at 20 MHz. Notebook 02 explained why echoes are so weak using the radar equation. Now we step across to the receive side and ask a simple question: once the pulse leaves the antenna, what comes back?

## The channel model in one picture

The channel is the path between the radar and the target. It does three things to the transmitted pulse:

1. **Delays it.** The pulse travels to the target and back, so the echo arrives later than the transmitted pulse by the round-trip time.
2. **Weakens it.** Only a tiny fraction of the transmitted energy reflects off the target and returns to the radar, so the echo is much weaker than the original.
3. **Corrupts it.** Thermal noise in the receiver adds random fluctuations that bury the echo, especially at long range.

The received signal during one PRI is therefore the transmitted pulse, shifted, scaled, and noise-boosted. That is the signal the radar must process to detect the target.

## Step 1: range to delay

The round-trip delay for a target at range $R$ is

$$
\tau_{delay} = \frac{2R}{c}
$$

and the corresponding sample delay at sampling rate $f_s$ is

$$
n_{delay} = \text{round}\!\left(\tau_{delay} \cdot f_s\right)
$$

You already saw this arithmetic in Notebook 00. Here we use it to place the echo in the right slot of the received signal buffer.

### Notebook cell 10 · code
```python
# Compute the sample delay for the baseline 1000 m target.
c = 299_792_458.0
target_range_m = radar_spec.target_range_m
n_delay = delay_samples_for_range(target_range_m, radar_spec.fs_hz)
delay_us = (2.0 * target_range_m / c) * 1e6
echo_end = n_delay + int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))

print(f"Target range = {target_range_m:.0f} m")
print(f"Round-trip delay = {delay_us:.2f} microseconds = {n_delay} samples")
print(f"Pulse length = {int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))} samples")
print(f"Echo ends at sample {echo_end} (buffer must be at least this long)")
```

**Executed output:**

```
Target range = 1000 m
Round-trip delay = 6.67 microseconds = 133 samples
Pulse length = 400 samples
Echo ends at sample 533 (buffer must be at least this long)
```

**What this cell does — Step 1: range becomes a sample delay.**

The delay arithmetic from Notebook 00, now on the receive side. The 1000 m target gives a round-trip delay of 6.67 microseconds, which is 133 samples at 20 MHz. The 400-sample pulse then occupies samples 133 through 532, so the received buffer must be at least 533 samples long.

This number - 133 samples - is the range measurement in disguise. Placing the echo in the right slot of the buffer is what the rest of the notebook does.

## Step 2: build the echo by shifting the transmitted pulse

The echo is a copy of the transmitted pulse, placed at the right delay in the received buffer. Before we add attenuation or noise, this is just a copy operation: write the pulse into the buffer starting at sample $n_{delay}$.

### Notebook cell 12 · code
```python
# Build a rectangular pulse and a clean echo buffer.
pulse = rectangular_pulse(int(round(radar_spec.pulse_width_s * radar_spec.fs_hz)))

# Received buffer is long enough to hold the delay plus the pulse.
received_len = n_delay + len(pulse)
clean_echo = np.zeros(received_len)
clean_echo[n_delay : n_delay + len(pulse)] = pulse

print(f"Transmitted pulse: {len(pulse)} samples, amplitude {pulse[0]}")
print(f"Received buffer: {received_len} samples")
print(f"Echo occupies samples {n_delay} to {n_delay + len(pulse) - 1}")
```

**Executed output:**

```
Transmitted pulse: 400 samples, amplitude 1.0
Received buffer: 533 samples
Echo occupies samples 133 to 532
```

**What this cell does — Step 2: place the echo by copying.**

The echo is a copy of the transmitted pulse, not a new waveform. This cell writes the 400-sample block into the buffer starting at sample 133. Transmitted pulse: 400 samples, amplitude 1.0. Received buffer: 533 samples, echo at samples 133 to 532.

Same shape, same length, different position. Only later do we scale it down and bury it in noise.

## Step 3: add attenuation

Notebook 02 explained why radar echoes are so weak using the radar equation — the signal spreads on the way out, reflects off the target, and spreads again on the way back, giving a 1 / R⁴ dependence. Here we turn that physics into a single number.

The radar equation combines transmitted power, antenna gain, wavelength, target cross section, and range into an attenuation factor. For the baseline 1000-metre target with plausible system parameters, the result is −40 dB. That means the echo amplitude is 10⁻⁴⁰/²⁰ = 0.01 times the transmitted amplitude — a hundred times weaker in amplitude, ten thousand times weaker in power.

We apply this as a single scaling factor. The shape of the echo does not change — only its amplitude.

### Notebook cell 14 · code
```python
# Apply a realistic attenuation to the echo.
attenuation_db = -40.0
attenuation_linear = 10.0 ** (attenuation_db / 20.0)

attenuated_echo = np.zeros(received_len)
attenuated_echo[n_delay : n_delay + len(pulse)] = attenuation_linear * pulse

print(f"Attenuation = {attenuation_db:.0f} dB (amplitude factor = {attenuation_linear:.4f})")
print(f"Transmitted amplitude = {pulse[0]}")
print(f"Echo amplitude = {attenuated_echo[n_delay]:.4f}")
```

**Executed output:**

```
Attenuation = -40 dB (amplitude factor = 0.0100)
Transmitted amplitude = 1.0
Echo amplitude = 0.0100
```

**What this cell does — Step 3: attenuation scales it down.**

Notebook 02's physics becomes one number. -40 dB turns into an amplitude factor of 10^(-40/20) = 0.01: the echo amplitude drops from 1.0 to 0.01, a hundred times in amplitude and ten-thousand times in power. The shape is untouched; only the size changes.

The y-axes in later plots hide this, so always check the numbers. 0.0100 next to 1.0 is the whole story of why echoes are hard to detect.

## Step 4: add noise

Every radar receiver has a thermal noise floor. We model this as additive white Gaussian noise (AWGN) with a power level set by the desired signal-to-noise ratio (SNR). At 20 dB SNR the signal power is 100 times the noise power — high enough to see the echo in a plot, but already low enough to show why the matched filter matters.

### Notebook cell 16 · code
```python
# Add noise to the attenuated echo.
snr_db = 20.0
echo_power = np.mean(attenuated_echo[n_delay : n_delay + len(pulse)] ** 2)
noise_power = echo_power / (10.0 ** (snr_db / 10.0))
noise = np.sqrt(noise_power) * np.random.randn(received_len)
noisy_received = attenuated_echo + noise

print(f"SNR = {snr_db:.0f} dB")
print(f"Echo power = {echo_power:.2e}")
print(f"Noise power = {noise_power:.2e}")
```

**Executed output:**

```
SNR = 20 dB
Echo power = 1.00e-04
Noise power = 1.00e-06
```

**What this cell does — Step 4: noise buries it.**

Receiver thermal noise modeled as additive white Gaussian noise. With SNR at 20 dB, noise power is the echo power divided by 100: echo power 1e-4, noise power 1e-6. The noise spreads across the whole 533-sample buffer and masks an echo concentrated in only 400 of them.

20 dB sounds strong, yet the next panel still looks noisy. That is the motivation for the matched filter: the echo is real, but no single sample is reliable proof of it.

## The transmitted pulse versus the received signal

The three-panel plot shows the full story, but you need to know where to look.

**Top panel: the transmitted pulse.** This is the clean waveform at full amplitude (1.0). It is what leaves the antenna.

**Middle panel: the attenuated echo.** This is the same shape, shifted in time and scaled down. Two things to notice: the echo starts at sample 133 (the delay encodes the range), and the amplitude is now 0.01 (the attenuation encodes the path loss). Check the y-axis — the scale has changed from [0, 1] to [−0.02, 0.02]. The visual size of the waveform looks similar to the top panel, but the numbers tell you it is 100 times smaller.

**Bottom panel: the noisy received signal.** The attenuated echo is still there, but receiver noise has been added on top. The signal is no longer a flat burst — it fluctuates across the entire buffer. Your eye can still pick out the general shape if you know where to look, but a detector cannot rely on that. The radar needs a systematic way to pull the echo out of the noise, which is what the matched filter does in Notebook 04.

Read the three panels as a sequence: transmit (top), weaken (middle), corrupt (bottom). The matched filter reverses this sequence — it takes the corrupted signal and recovers the echo location.

### Notebook cell 18 · code
```python
# Plot transmitted pulse, attenuated echo, and noisy received signal.
fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
time_received = np.arange(received_len) / radar_spec.fs_hz * 1e6
time_pulse = np.arange(len(pulse)) / radar_spec.fs_hz * 1e6

axes[0].plot(time_pulse, pulse, color="#d95f02", label="Transmitted pulse")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Transmitted pulse")
axes[0].legend(loc="upper right")

axes[1].plot(time_received, attenuated_echo, color="#1b9e77", label="Attenuated echo")
axes[1].set_ylabel("Amplitude")
axes[1].set_title(f"Echo after {attenuation_db:.0f} dB attenuation")
axes[1].legend(loc="upper right")

axes[2].plot(time_received, noisy_received, color="#7570b3", label="Noisy received signal", linewidth=0.7)
axes[2].set_ylabel("Amplitude")
axes[2].set_xlabel("Time within the receive window (microseconds)")
axes[2].set_title(f"Receiver output at {snr_db:.0f} dB SNR — echo buried in noise")
axes[2].legend(loc="upper right")

plt.tight_layout()
plt.show()

print("The echo is there, but hard to see in the bottom panel.")
print("Notebook 04 will show how the matched filter pulls it out.")
```

**Executed output:**

```
<Figure size 1000x600 with 3 Axes>
The echo is there, but hard to see in the bottom panel.
Notebook 04 will show how the matched filter pulls it out.
```

![Notebook output](assets/03/fig_cell18_0.png)

**What this cell does — The transmitted pulse versus the received signal.**

The notebook's one summary picture, read left to right. Top: the clean transmitted pulse at amplitude 1. Middle: the attenuated echo, same shape at sample 133, amplitude 0.01. Bottom: the noisy received signal at 20 dB SNR, where the echo is present but no longer obvious.

The middle panel's y-axis has already shrunk to about -0.02 to +0.02; the bottom panel adds fluctuations on top. Transmit, weaken, corrupt - and Notebook 04 runs the sequence backwards.

## Stretch exercise: a second target

A radar rarely sees just one target. To understand what two echoes look like, build the received signal step by step.

The first plot shows the two echoes individually — each is a clean, attenuated copy of the transmitted pulse at its own delay. In this example the second echo starts (sample 400) before the first echo ends (sample 533), so the two pulses **overlap** by 134 samples.

The second plot shows what actually arrives at the receiver: the sum of the two echoes. You can still make out two steps — one at sample 133 and another at sample 400 — because the pulses are long and the gap between their starts is comparable to the pulse length. But notice how a radar that measures *only the start of the received burst* would stop at sample 133 and report a single target. It would never see the second echo, because that energy is hiding inside the first pulse's duration.

The third plot shows the noisy version. Now the clean step at sample 400 is buried — the noise turns the whole region into a bumpy fluctuation with no obvious edge. This is the real ambiguity: at a glance you cannot tell whether there is one target or two, let alone where the second one begins. Later notebooks resolve this with the matched filter.

### Notebook cell 20 · code
```python
# Optional: add a second target at 3000 m.
# The two echoes overlap in time, so when summed they look like a single long pulse.
second_range_m = 3000.0
n_delay_2 = delay_samples_for_range(second_range_m, radar_spec.fs_hz)

# Buffer long enough to hold both echoes.
two_target_len = n_delay_2 + len(pulse)

# Build each echo individually.
first_echo = np.zeros(two_target_len)
first_echo[n_delay : n_delay + len(pulse)] = attenuation_linear * pulse

second_echo = np.zeros(two_target_len)
second_echo[n_delay_2 : n_delay_2 + len(pulse)] = attenuation_linear * pulse

# The receiver sees their sum.
two_target_clean = first_echo + second_echo

# Add noise.
echo_power_2 = np.mean(two_target_clean[n_delay : n_delay + len(pulse)] ** 2)
noise_power_2 = echo_power_2 / (10.0 ** (snr_db / 10.0))
two_target_noisy = two_target_clean + np.sqrt(noise_power_2) * np.random.randn(two_target_len)

print(f"First target  = {radar_spec.target_range_m:.0f} m, delay = {n_delay} samples (echo: {n_delay}-{n_delay + len(pulse)})")
print(f"Second target = {second_range_m:.0f} m, delay = {n_delay_2} samples (echo: {n_delay_2}-{n_delay_2 + len(pulse)})")
print(f"They overlap from sample {n_delay_2} to {n_delay + len(pulse)}, so the sum looks like one long pulse.")

time_axis_2 = np.arange(two_target_len) / radar_spec.fs_hz * 1e6

# Panel 1: the two echoes drawn individually.
fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)

axes[0].plot(time_axis_2, first_echo + second_echo, color="#e6e6e6", linewidth=1.0, zorder=1)
axes[0].plot(time_axis_2, first_echo, color="#1b9e77", linewidth=1.2, label="Echo from 1000 m")
axes[0].plot(time_axis_2, second_echo, color="#d95f02", linewidth=1.2, label="Echo from 3000 m")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("The two echoes, drawn separately (their sum shown faintly)")
axes[0].legend(loc="upper right")

# Panel 2: the summed signal (clean).
axes[1].plot(time_axis_2, two_target_clean, color="#1b9e77", linewidth=1.2)
axes[1].set_ylabel("Amplitude")
axes[1].set_title("Summed signal: two steps still visible, but a leading-edge detector reads only the first")

# Panel 3: the noisy summed signal.
axes[2].plot(time_axis_2, two_target_noisy, color="#7570b3", linewidth=0.7)
axes[2].set_ylabel("Amplitude")
axes[2].set_xlabel("Time within the receive window (microseconds)")
axes[2].set_title("Same sum with noise: the second step is buried — one target or two?")

plt.tight_layout()
plt.show()
```

**Executed output:**

```
First target  = 1000 m, delay = 133 samples (echo: 133-533)
Second target = 3000 m, delay = 400 samples (echo: 400-800)
They overlap from sample 400 to 533, so the sum looks like one long pulse.
<Figure size 1000x700 with 3 Axes>
```

![Notebook output](assets/03/fig_cell20_0.png)

**What this cell does — Stretch: two overlapping echoes.**

A second target at 3000 m arrives at sample 400 and ends at 800, while the first echo occupies samples 133 to 533: they overlap from 400 to 533, and the sum looks like one long pulse. In the noisy version the second 'step' disappears into the fluctuation.

This is real radar ambiguity: a leading-edge detector reading only the first rise reports one target at 1000 m and misses the second. The matched filter later separates them by collapsing each echo to its own peak.

## Checkpoint

In your own words, what are the three things the channel does to the transmitted pulse?

Then answer this: if you doubled the target range while keeping everything else fixed, what would happen to the sample delay and to the echo amplitude?

## Common mistake

A common mistake is to think the echo is a different waveform from the transmitted pulse. It is not. The echo is a copy — same shape, same length — just shifted in time and scaled down. The noise added by the receiver is what makes it look different, not the channel itself.

Another mistake is to treat attenuation and noise as the same thing. Attenuation is a deterministic scaling: the echo is smaller but still clean. Noise is random: it adds fluctuations that corrupt the signal. The matched filter in Notebook 04 exploits the fact that the echo is a known shape buried in uncorrelated noise.

## Why the helpers exist

The cells above build the channel model step by step so you can see each operation — delay, attenuation, noise — happen individually. After that first pass, the same logic moves into the helper package so later notebooks can create a received signal in one call without repeating the derivation.

The helper functions are:

- `add_echo(signal, template, delay_samples, attenuation_linear)` — places a delayed, attenuated copy of the template into the signal.
- `awgn(signal, snr_db)` — adds white Gaussian noise to achieve the desired SNR.
- `single_target_channel(transmitted, delay_samples, attenuation_linear, snr_db)` — the full pipeline in one call.

As in the earlier notebooks, keep the first occurrence visible so you see the physics, then use the helpers when you want the lesson to stay readable.

### Notebook cell 24 · code
```python
# Now use the helper functions to reproduce the same channel model compactly.
from beginner.helpers import single_target_channel, add_echo, awgn

helper_spec = baseline_spec()
helper_pulse = rectangular_pulse(int(round(helper_spec.pulse_width_s * helper_spec.fs_hz)))
helper_delay = delay_samples_for_range(helper_spec.target_range_m, helper_spec.fs_hz)
helper_received = single_target_channel(helper_pulse, helper_delay, attenuation_linear, snr_db)

print(f"Helper-based channel output: {len(helper_received)} samples")
print(f"Echo at sample {helper_delay}, pulse length {len(helper_pulse)}")
print(f"Peak of received signal around echo: {np.max(np.abs(helper_received[helper_delay:helper_delay+len(helper_pulse)])):.4f}")
```

**Executed output:**

```
Helper-based channel output: 533 samples
Echo at sample 133, pulse length 400
Peak of received signal around echo: 0.0128
```

**What this cell does — The channel model, one call.**

All three operations - delay, attenuation, noise - now come from the single_target_channel helper: 533 samples, echo at sample 133, 400-sample pulse, and a peak of 0.0128 in the echo region. One line reproduces the whole multi-step channel.

0.0128, not 0.01, because the noise on top nudges the observed peak. The helper is what later notebooks use to build received signals without repeating the construction.

## Closing the loop: answers to the opening questions

At the start of this notebook we listed four things you should be able to explain. Here is a direct answer to each one, using the physics, equations, and numbers we just worked through.

### How range turns into a sample delay

A target at range $R$ produces a round-trip delay of $2R/c$, and the sampling clock chops that delay into discrete samples at rate $f_s$. For the baseline 1000 m target the delay is $2 \times 1000 / c$, about 6.67 microseconds, which spans133 samples at 20 MHz. The `delay_samples_for_range` helper returns exactly that number, and you used it here to know where in the received buffer to write the echo.

### What an echo looks like relative to the transmitted pulse

The echo is a copy of the transmitted pulse — same shape, same length — just shifted in time by the sample delay and scaled down by the attenuation factor. In the middle panel of the three-part plot, the attenuated echo looks like a small replica of the transmitted pulse sitting in the right slot. The waveform itself does not change; only its position and size do.

### Why attenuation makes the echo weaker

Attenuation accounts for the round-trip path loss, target reflectivity, and system losses combined. At -40 dB the echo amplitude is 0.01 times the transmitted amplitude — the middle panel shows it clearly. The bottom panel then adds noise, and the echo disappears into the fluctuations. That is the core problem: the echo is real but too weak to see without processing.

### How noise hides the echo and motivates the matched filter

Thermal noise in the receiver adds random fluctuations at a power level set by the SNR. At 20 dB the signal is 100 times stronger than the noise in power, but because the noise is spread across the whole buffer while the echo is concentrated in a short slot, the echo can still be hard to spot by eye in the bottom panel. The matched filter in Notebook 04 solves exactly this: it correlates the received signal with the known transmitted shape, collapsing the echo into a sharp peak while the uncorrelated noise stays spread out.

If you can retell these four answers in your own words — how delay relates to range, what the echo looks like, why it is weak, and why the matched filter is needed — you have the message of this notebook.

## Summary

In this notebook you stepped across to the receive side and built the channel model that sits between the transmitted pulse and the radar receiver. The channel does three things: it delays the pulse by the round-trip travel time, it weakens it by the path and target losses, and it adds noise from the receiver electronics.

The delay is the range measurement in disguise — it is the same `delay_samples_for_range` calculation from Notebook 00, now used to place a real echo in the received buffer. Attenuation and noise are what make the echo hard to see without processing, and together they motivate the matched filter that Notebook 04 will introduce.

The main takeaway is that the received signal is not a mystery: it is a known transmitted waveform, shifted and scaled, buried in noise. The radar's job is to pull it out, and the matched filter is the tool that does it.
