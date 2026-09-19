# Walkthrough — 00: Radar Intuition and Baseline Parameters

This is a cell-by-cell walkthrough of `beginner/notebooks/00-radar-intuition.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 00 — Radar Intuition and Baseline Parameters

This notebook explains what pulse radar is, why the quiet listening interval matters, and why the baseline radar parameters were chosen.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/00-radar-intuition.ipynb)

Use this link if you want to open the notebook in Colab and follow along in a browser notebook environment.

### Notebook cell 2 · code
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

This first cell makes your environment match ours. In Colab it clones the repository, installs the beginner package, and switches into the workspace. Running locally it simply confirms where the notebook is working and adds the repository root to the import path. Run it once and it quietly sets up everything later cells need.

You never have to touch this cell again. Think of it as the notebook's door: it gets you into the same well-known room regardless of whether you arrived in a browser or on your own machine, and then it steps out of the way.

## What this notebook teaches

Pulse radar is a system that transmits a short burst of energy, then stops transmitting and listens for the echo. That simple idea drives everything that follows in this course.

By the end of this notebook, you should be able to explain:

- what pulse radar is,
- why the radar listens after it transmits,
- how duty cycle is computed,
- and how a range delay turns into a range estimate.

Keep these four questions in mind as you work through the cells. At the end of the notebook, a dedicated section answers each one directly, so you can study the material first and then check your understanding against the full story.

## Setup and baseline values

Before we calculate anything, we load the small beginner helper package and create one named baseline radar specification. If you are running this notebook in Colab, run the bootstrap cell above first so the repository is cloned, installed, and available for import.

### Notebook cell 5 · code
```python
import matplotlib.pyplot as plt

from beginner.helpers import BaselineRadarSpec, baseline_spec, duty_cycle, delay_samples_for_range, range_from_delay_samples, wavelength_m
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

**What this cell does — Setup: load the helper package and the baseline spec.**

We load the plotting style and the helper functions, then create one named radar specification. The final expression displays the object itself, and that listing is the entire baseline reference set for the beginner track: 2.45 GHz carrier, 5 MHz bandwidth, 20 microsecond pulse width, 1 millisecond PRI, 20 MHz sampling rate, and a target at 1000 m.

Every later notebook starts from this exact object. Fixing one named baseline keeps the numbers consistent across lessons: when a later notebook says the target is 1000 m away or the pulse is 20 microseconds, it is echoing this same specification.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Baseline radar reference

The baseline radar specification is the fixed example we use throughout the beginner lessons. Each number has a job to do, and this table explains what each one controls.

| Quantity | Value | What it controls |
|---|---:|---|
| Carrier frequency | 2.45 GHz | Connects the radar to wavelength and later Doppler calculations |
| Bandwidth | 5 MHz | Sets the range resolution we can achieve with pulse compression |
| Pulse width | 20 microseconds | Controls how long each burst is transmitted |
| PRI | 1 millisecond | Sets how long the radar has to listen before the next pulse |
| Sampling rate | 20 MHz | Tells us how many samples we record per second |
| Target range | 1000 m | Gives us one concrete delay-to-range example |

## What pulse radar means

A pulse radar does not transmit continuously. It sends a short burst of energy and then waits. During the transmit burst, the antenna is busy sending power out. During the quiet time after the burst, the radar listens for the echo that comes back from a target.

This back-and-forth rhythm is the foundation of range measurement:

- the transmitted pulse creates the event,
- the quiet listening window lets the echo arrive,
- the time delay of that echo tells us how far away the target is.

The important idea is that the radar is not trying to hear while it is speaking. It has to stop transmitting before it can listen clearly.

## Why the radar listens after it transmits

The radar needs a quiet interval because the echo from a distant target takes time to come back. If the radar kept transmitting continuously, the weak echo would be buried under the outgoing signal.

That is why we define a pulse repetition interval, or PRI. The pulse width is the short transmit burst, and the rest of the PRI is the listening window.

The key equations are:

$$
D = \frac{\tau}{T}
$$

for duty cycle, and

$$
R = \frac{c \cdot \tau_{delay}}{2}
$$

for range from round-trip delay.

In this notebook, we use the baseline values to compute those quantities explicitly so you see the arithmetic before the helper functions are introduced.

### Notebook cell 10 · code
```python
# Compute the lesson quantities step by step with the equations written out in the notebook.
duty_cycle_value = radar_spec.pulse_width_s / radar_spec.pri_s
round_trip_delay_seconds = (2.0 * radar_spec.target_range_m) / 299_792_458.0
round_trip_delay_samples = round(round_trip_delay_seconds * radar_spec.fs_hz)
estimated_range_m = (round_trip_delay_samples / radar_spec.fs_hz) * 299_792_458.0 / 2.0
carrier_wavelength_m = 299_792_458.0 / radar_spec.fc_hz

print("Baseline radar values used in this lesson:")
print(f"  carrier frequency = {radar_spec.fc_hz / 1e9:.2f} GHz")
print(f"  bandwidth = {radar_spec.bandwidth_hz / 1e6:.1f} MHz")
print(f"  pulse width = {radar_spec.pulse_width_s * 1e6:.1f} microseconds")
print(f"  PRI = {radar_spec.pri_s * 1e3:.1f} milliseconds")
print(f"  sampling rate = {radar_spec.fs_hz / 1e6:.1f} MHz")
print()
print("Step 1: duty cycle = pulse width / PRI")
print(f"  duty cycle = {radar_spec.pulse_width_s:.2e} / {radar_spec.pri_s:.2e} = {duty_cycle_value:.3f}")
print()
print("Step 2: round-trip delay = 2 * range / speed of light")
print(f"  delay = 2 * {radar_spec.target_range_m:.1f} / 299,792,458 = {round_trip_delay_seconds:.3e} s")
print(f"  delay = {round_trip_delay_samples} samples at {radar_spec.fs_hz / 1e6:.1f} MHz")
print()
print("Step 3: convert delay back to range")
print(f"  estimated range = {estimated_range_m:.1f} m")
print()
print("Step 4: carrier wavelength")
print(f"  wavelength = {carrier_wavelength_m:.4f} m")
```

**Executed output:**

```
Baseline radar values used in this lesson:
  carrier frequency = 2.45 GHz
  bandwidth = 5.0 MHz
  pulse width = 20.0 microseconds
  PRI = 1.0 milliseconds
  sampling rate = 20.0 MHz

Step 1: duty cycle = pulse width / PRI
  duty cycle = 2.00e-05 / 1.00e-03 = 0.020

Step 2: round-trip delay = 2 * range / speed of light
  delay = 2 * 1000.0 / 299,792,458 = 6.671e-06 s
  delay = 133 samples at 20.0 MHz

Step 3: convert delay back to range
  estimated range = 996.8 m

Step 4: carrier wavelength
  wavelength = 0.1224 m
```

**What this cell does — The physics by hand, before any helper.**

This cell does the core arithmetic with the equations written out in plain view. Step 1 computes duty cycle as pulse width over PRI: 20 microseconds over 1 millisecond is 0.020, so the radar transmits only 2 percent of the time. Step 2 finds the round-trip delay for a 1000 m target: 2 x 1000 divided by the speed of light, about 6.67 microseconds, which is 133 samples at 20 MHz. Step 3 runs the equation backwards and gets an estimated range of 996.8 m, and Step 4 derives the carrier wavelength of 0.1224 m.

Notice the small gap between 1000 m and 996.8 m. The true echo delay falls between two sample times, so the measurement must land on the nearest sample. This is sample quantization, not a physics error, and it previews the range resolution idea that pulse compression later improves.

## Checkpoint

In your own words, why does a pulse radar need a listening window after the transmit pulse?

Then answer this: if the pulse width stays the same but the PRI becomes longer, what happens to the duty cycle?

The plot below shows one complete PRI for the baseline radar. 
The narrow orange bar is the transmit pulse (20 microseconds), 
and the wide green bar is the listening window (980 microseconds). 
The radar is off for 98 percent of each cycle.

### Notebook cell 13 · code
```python
# Draw a simple timing picture that shows when the radar transmits and when it listens.
fig, ax = plt.subplots(figsize=(10, 2.5))

ax.broken_barh([(0, radar_spec.pulse_width_s)], (0.25, 0.35), facecolors="#d95f02", label="Transmit pulse")
ax.broken_barh([(radar_spec.pulse_width_s, radar_spec.pri_s - radar_spec.pulse_width_s)], (0.25, 0.35), facecolors="#1b9e77", label="Listening window")

ax.text(radar_spec.pulse_width_s / 2, 0.7, "Transmit", ha="center", va="bottom")
ax.text(radar_spec.pulse_width_s + (radar_spec.pri_s - radar_spec.pulse_width_s) / 2, 0.7, "Listen", ha="center", va="bottom")

ax.set_xlim(0, radar_spec.pri_s)
ax.set_ylim(0, 1)
ax.set_xlabel("Time within one PRI (seconds)")
ax.set_yticks([])
ax.set_title("Pulse radar transmits briefly, then listens for the echo")
ax.legend(loc="upper right")

plt.show()
```

**Executed output:**

```
<Figure size 1000x250 with 1 Axes>
```

![Notebook output](assets/00/fig_cell13_0.png)

**What this cell does — One picture: the transmit-and-listen rhythm.**

This cell draws one complete pulse repetition interval. The short orange bar is the 20-microsecond transmit burst; the wide green bar is the 980-microsecond listening window that fills the rest of the millisecond.

Read the plot as the central idea of pulse radar: the radar stops speaking so it can hear. The transmit is a brief event, the listening is the long quiet stretch, and the echo arrives somewhere inside that green interval. Range measurement lives entirely in the listening part.

## Common mistake

A longer PRI does not make the radar transmit more often. 
It actually gives the radar more time to listen, so the duty cycle gets smaller. 
That is why a pulse radar can be active for only a small fraction of the time 
but still gather useful range information.

Another common mistake is to treat the delay as a technical detail instead of the main measurement. 
In pulse radar, the delay **is** the measurement — it is the raw observable that gives you distance. 
Everything else in the signal processing chain exists to make that one number more accurate.

### Notebook cell 15 · code
```python
# Show how a longer PRI shrinks the duty cycle.
baseline_duty = duty_cycle(radar_spec.pulse_width_s, radar_spec.pri_s)
longer_pri = 2.0 * radar_spec.pri_s  # double the PRI
longer_duty = duty_cycle(radar_spec.pulse_width_s, longer_pri)

print(f"Baseline PRI  = {radar_spec.pri_s * 1e3:.1f} ms  ->  duty cycle = {baseline_duty:.3f}")
print(f"Longer PRI    = {longer_pri * 1e3:.1f} ms  ->  duty cycle = {longer_duty:.3f}")
print()
print(f"Doubling the PRI halves the duty cycle from {baseline_duty:.3f} to {longer_duty:.3f}.")
print("The radar transmits less often, but listens longer each time.")
```

**Executed output:**

```
Baseline PRI  = 1.0 ms  ->  duty cycle = 0.020
Longer PRI    = 2.0 ms  ->  duty cycle = 0.010

Doubling the PRI halves the duty cycle from 0.020 to 0.010.
The radar transmits less often, but listens longer each time.
```

**What this cell does — The common mistake, made visible.**

This cell doubles the PRI from 1 millisecond to 2 milliseconds while keeping the pulse width fixed. The duty cycle halves from 0.020 to 0.010.

A longer PRI does not make the radar transmit more often; it gives the radar more listening time. The printed numbers make the relationship unmistakable: transmit activity is set by the pulse width, and the PRI only decides how much quiet time surrounds it.

## Why the helpers exist

The calculation above shows the equations directly so you can see the arithmetic happen. After that first pass, we move the same logic into the helper package so the later notebooks can reuse it without repeating the derivation.

That is what the helper functions are for:

- they keep the same baseline formulas available in later notebooks,
- they reduce repeated code,
- and they make later lesson cells shorter once you already understand the idea.

Going forward, use the helpers when you want the lesson to stay readable, but keep the first occurrence of a concept visible in the notebook itself. Once you have seen the equation work by hand, the helper version is the clean way to reuse the same idea.

### Notebook cell 17 · code
```python
# Now use the helper functions and the shared baseline spec to show the same answers more compactly.
helper_radar_spec = baseline_spec()
helper_duty_cycle_value = duty_cycle(helper_radar_spec.pulse_width_s, helper_radar_spec.pri_s)
helper_round_trip_delay_samples = delay_samples_for_range(helper_radar_spec.target_range_m, helper_radar_spec.fs_hz)
helper_estimated_range_m = range_from_delay_samples(helper_round_trip_delay_samples, helper_radar_spec.fs_hz)
helper_carrier_wavelength_m = wavelength_m(helper_radar_spec.fc_hz)

print("Helper-based version of the same calculations:")
print(f"  duty cycle = {helper_duty_cycle_value:.3f}")
print(f"  delay samples = {helper_round_trip_delay_samples}")
print(f"  estimated range = {helper_estimated_range_m:.1f} m")
print(f"  wavelength = {helper_carrier_wavelength_m:.4f} m")
```

**Executed output:**

```
Helper-based version of the same calculations:
  duty cycle = 0.020
  delay samples = 133
  estimated range = 996.8 m
  wavelength = 0.1224 m
```

**What this cell does — The same answers from the shared helpers.**

The identical five numbers now come from the helper package: duty cycle 0.020, 133 delay samples, an estimated range of 996.8 m, and a wavelength of 0.1224 m. Same equations, same results, cleaner code.

This is the pattern the course uses everywhere. You saw the arithmetic once with the physics visible. From here on, the helper is the clean, reusable version, and later notebooks build on it without repeating the derivation.

## Closing the loop: answers to the opening questions

At the start of this notebook we listed four things you should be able to explain. Here is a direct answer to each one, written as a short story that uses the physics, equations, and numbers we just worked through.

### What pulse radar is

Pulse radar is a distance sensor built out of careful timing. The radar transmits a short burst of energy toward the scene, then goes quiet and waits for some of that energy to reflect off a target and return as an echo. Because the radar knows exactly when it transmitted and how fast the energy travels, the returning echo carries a measurement. That is the whole system: transmit, listen, and time the return. The timing diagram near the end of the notebook shows this rhythm in one picture — a brief orange transmit pulse followed by a long green listening window.

### Why the radar listens after it transmits

The echo from a distant target takes time to come back, and while the transmitter is on, its own outgoing signal drowns out everything else. The radar cannot hear a faint echo while it is still speaking. That is why the pulse repetition interval exists: the PRI is one cycle of speak-then-listen, where the pulse width is the speaking part and the remaining quiet stretch is the listening part. With our baseline values, the radar transmits for 20 microseconds and then listens for the remaining 980 microseconds of each 1 millisecond PRI. The listening window is not idle time; it is when the measurement actually happens.

### How duty cycle is computed

Duty cycle answers the question: what fraction of the time is this radar transmitting? It is the pulse width divided by the PRI:

$$
D = \frac{\tau}{T} = \frac{20\ \mu s}{1\ ms} = 0.02
$$

You saw this computed by hand in Step 1 of the calculation cell, and again through the `duty_cycle` helper in the compact cell below it. A duty cycle of 0.02 means the radar spends only 2 percent of its time transmitting and 98 percent listening. This also explains why the common mistake above matters: lengthening the PRI does not increase transmit activity, it increases listening time, so the duty cycle shrinks.

### How a range delay turns into a range estimate

The echo delay is the measurement; range is what we compute from it. The round-trip relationship is:

$$
R = \frac{c \cdot \tau_{delay}}{2}
$$

We run this chain forward and backward in Steps 2 and 3 of the calculation cell. A target at 1000 m produces a delay of $2 \times 1000 / c$, about 6.67 microseconds. At our sampling rate of 20 MHz, that delay spans roughly 133 samples. Converting those samples back with the same equation gives an estimated range of 996.8 m rather than exactly 1000 m, because the true delay falls between two sample boundaries and must land on a sample. That small gap is not an error in the physics; it is sample quantization, and it previews the idea that resolution is limited by how finely we can measure the delay.

If you can retell these four answers in your own words — what the system is, why it listens, how busy it is while transmitting, and how delay becomes range — you have the message of this notebook.

## Summary

In this notebook, you met pulse radar as a simple but powerful idea: transmit a short burst, wait quietly, and use the returning echo to measure range. The lesson showed that the listening window is not an optional extra; it is the part of the radar cycle that makes the measurement possible.

The notebook also introduced the baseline radar example used throughout the beginner track. That shared example gives the course a common set of radar values so each later notebook can build on the same physical situation. From here forward, you should think of those values as the reference case that connects the radar story across range, timing, Doppler, and the later application notebooks.

The main takeaway is that radar is not just about transmitting energy. It is about carefully timing the transmit-and-listen cycle so the system can turn a delay into a physical measurement with meaning.
