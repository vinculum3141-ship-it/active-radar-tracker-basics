# Walkthrough — 02: The Radar Equation

This is a cell-by-cell walkthrough of `beginner/notebooks/02-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 02 — The Radar Equation

This notebook explains why radar echoes are so weak and how the radar equation connects transmitted power, range, and target properties to the received signal level.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/02-radar-equation.ipynb)

Use this link if you want to open the notebook in Colab and follow along in a browser notebook environment.

## What this notebook teaches

By the end of this notebook, you should be able to explain:

- why radar echoes are billions of times weaker than the transmitted pulse,
- what the radar equation says and what each term means,
- why received power falls as the fourth power of range,
- and how the −40 dB attenuation used in later notebooks comes from the physics.

## Setup and baseline values

The bootstrap cell below clones the repository and installs the helper package if you are running in Colab. If you are running locally, it adds the repository root to the Python path so the imports work.

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

from beginner.helpers.constants import BaselineRadarSpec
from beginner.helpers.constants import baseline_spec
from beginner.helpers.math import wavelength_m
from beginner.helpers.plotting import apply_notebook_style

apply_notebook_style()

radar_spec = baseline_spec()

print(f"Carrier frequency = {radar_spec.fc_hz / 1e9:.2f} GHz")
print(f"Wavelength         = {wavelength_m(radar_spec.fc_hz):.4f} m")
print(f"Target range       = {radar_spec.target_range_m:.0f} m")
```

**Executed output:**

```
Carrier frequency = 2.45 GHz
Wavelength         = 0.1224 m
Target range       = 1000 m
```

**What this cell does — Setup: constants and wavelength.**

This cell loads the baseline specification and one math helper. It prints the carrier frequency 2.45 GHz, the wavelength 0.1224 m (speed of light divided by carrier frequency), and the baseline target range of 1000 m. These are the numbers the radar equation needs from our specification.

The wavelength is computed by a helper rather than hard-coded, so it can never drift out of agreement with the carrier frequency across lessons.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

Notebooks 00 and 01 built the transmit side: the pulse shape, the chirp, and the resolution properties. Now we step across to the link between transmitter and receiver and ask: once the pulse leaves the antenna, how much energy actually comes back?

The answer is: almost none. The radar equation explains why.

## Why the echo is so weak

When the radar transmits, the energy spreads outward in all directions like the surface of an expanding sphere. Only a tiny fraction of that energy hits the target. The target reflects some of it, again spreading in all directions. Only a tiny fraction of the reflected energy heads back toward the radar. And by the time it arrives, it has traveled twice the distance.

There are four separate losses at work:

1. **Outward spreading.** The transmitted power density at the target falls as 1 / R², where R is the range.
2. **Target interception.** The target intercepts only the power that falls on its effective area, called the radar cross section (σ).
3. **Return spreading.** The reflected energy spreads outward again, and the power density at the radar falls as 1 / R² a second time.
4. **System losses.** The transmitter, antenna, receiver, and propagation medium all introduce losses.

Combining the two spreading losses gives the characteristic 1 / R⁴ dependence. That is why radar echoes are so much weaker than the transmitted pulse.

## The radar equation

The monostatic radar equation relates the received power to the transmitted power and the system parameters:

$$
P_r = \frac{P_t \, G_t \, G_r \, \lambda^2 \, \sigma}{(4\pi)^3 \, R^4 \, L}
$$

where:

| Symbol | Meaning |
|--------|---------|
| $P_r$ | Received power (what the radar detects) |
| $P_t$ | Transmitted power (what the radar puts out) |
| $G_t$ | Transmitting antenna gain (how much the antenna concentrates the beam) |
| $G_r$ | Receiving antenna gain |
| $\lambda$ | Wavelength of the carrier frequency |
| $\sigma$ | Target radar cross section (effective reflecting area) |
| $R$ | Range to the target |
| $L$ | Combined system losses |

For a radar that uses the same antenna for transmit and receive, $G_t = G_r = G$, and the equation simplifies to:

$$
P_r = \frac{P_t \, G^2 \, \lambda^2 \, \sigma}{(4\pi)^3 \, R^4 \, L}
$$

The $R^4$ in the denominator is the key. Doubling the range does not halve the received power — it reduces it by a factor of 16.

## The 1 / R⁴ dependence

The fourth-power law is the most important feature of the radar equation. It comes from the signal making a round trip: the power falls as 1 / R² on the way out and 1 / R² on the way back.

The plot below shows how received power drops with range on a log–log scale, normalised to 1 at the closest range (200 m). At the baseline target range of 1000 m — five times further — the received power is 1/5⁴ = 1/625 of the power at 200 m. That is a factor of 625 for just a fivefold increase in range.

### Notebook cell 11 · code
```python
# Show the 1/R^4 dependence on a log-log scale.
ranges = np.linspace(200, 5000, 500)
relative_power = 1.0 / ranges**4
relative_power /= relative_power[0]  # normalise to 1 at the closest range

fig, ax = plt.subplots(figsize=(8, 4))
ax.loglog(ranges, relative_power, color="#d95f02", linewidth=2)
ax.set_xlabel("Range (m)")
ax.set_ylabel("Relative received power")
ax.set_title("Received power falls as 1 / R\u2074")
ax.grid(True, which="both", linestyle="--", alpha=0.5)

# Mark the baseline target
baseline_idx = np.argmin(np.abs(ranges - radar_spec.target_range_m))
ax.plot(radar_spec.target_range_m, relative_power[baseline_idx], "ko", markersize=8)
ax.annotate(
    f"{radar_spec.target_range_m:.0f} m",
    (radar_spec.target_range_m, relative_power[baseline_idx]),
    textcoords="offset points", xytext=(10, 10), fontsize=10,
)

plt.tight_layout()
plt.show()
```

**Executed output:**

```
/var/folders/5s/tqh7ypys04v9bjhvzfpb_llc0000gn/T/ipykernel_23555/2020469386.py:22: UserWarning: Glyph 8308 (\N{SUPERSCRIPT FOUR}) missing from font(s) Arial.
  plt.tight_layout()
/Users/ruby/Projects/active-radar-tracker-basics/.venv/lib/python3.12/site-packages/IPython/core/pylabtools.py:158: UserWarning: Glyph 8308 (\N{SUPERSCRIPT FOUR}) missing from font(s) Arial.
  fig.canvas.print_figure(bytes_io, **kw)
<Figure size 800x400 with 1 Axes>
```

![Notebook output](assets/02/fig_cell11_0.png)

**What this cell does — The 1/R⁴ curve.**

The famous fourth-power curve, plotted on a log-log scale. Relative received power is 1/R⁴, normalized to 1 at the closest range of 200 m. The black dot and label mark the baseline target at 1000 m, five times further out.

Read the drop: from 200 to 1000 m, five times the range, the received power falls to 1/5⁴ = 1/625 of the closer value. On a log-log plot a power law is a straight line, and this one has slope -4.

## What each term controls

Before plugging in numbers, it is worth understanding what the radar designer can control and what comes from the target.

**Transmitted power ($P_t$).** More power means a stronger echo, but higher power costs more electricity, requires heavier hardware, and makes the radar easier to detect. Real radars choose $P_t$ to meet a range requirement within the available power budget.

**Antenna gain ($G$).** Gain measures how much the antenna concentrates energy in one direction compared with an isotropic (equal in all directions) antenna. A high-gain antenna sends more energy toward the target and collects more on the return, but it covers a smaller patch of sky.

**Wavelength ($\lambda$).** The wavelength appears because it sets the effective collecting area of the antenna. For a fixed antenna size, a shorter wavelength gives higher gain. The wavelength also affects how the target reflects energy, which is captured in the radar cross section.

**Radar cross section ($\sigma$).** This is the target property. It measures how much energy the target reflects back toward the radar, expressed as an equivalent area in square metres. A large aircraft might have a radar cross section of 100 m²; a small drone might be 0.01 m². The radar equation treats the target as a point that intercepts and re-radiates energy.

**Range ($R$).** The radar equation shows how received power depends on range. This is not something the designer chooses — it is the variable the radar is trying to measure.

## Computing the round-trip loss by hand

Rather than compute absolute power in watts (which would require knowing the transmitter power, antenna gain, and losses), it is more instructive to compute the round-trip loss factor for the baseline target. This is the fraction of transmitted power that returns as the echo.

The round-trip loss combines the spreading loss and the target interception into a single ratio. For a target at range $R$ with radar cross section $\sigma$, the loss factor is:

$$
\text{loss factor} = \frac{\sigma \, \lambda^2}{(4\pi)^3 \, R^4}
$$

This does not include antenna gain or transmitter power — it isolates the geometric spreading and target reflection.

### Notebook cell 14 · code
```python
# Compute the round-trip loss factor for the baseline target.
lam = wavelength_m(radar_spec.fc_hz)
R = radar_spec.target_range_m
sigma = 1.0  # 1 m^2 target radar cross section

loss_factor = (sigma * lam**2) / ((4 * np.pi)**3 * R**4)
loss_db = 10 * np.log10(loss_factor)

print(f"Wavelength       = {lam:.4f} m")
print(f"Range            = {R:.0f} m")
print(f"RCS              = {sigma:.1f} m^2")
print()
print(f"Round-trip loss  = {loss_factor:.2e}")
print(f"                  = {loss_db:.1f} dB")
print()
print(f"Only {loss_factor:.2e} of the transmitted power density")
print(f"returns from a 1 m^2 target at {R:.0f} m.")
```

**Executed output:**

```
Wavelength       = 0.1224 m
Range            = 1000 m
RCS              = 1.0 m^2

Round-trip loss  = 7.55e-18
                  = -171.2 dB

Only 7.55e-18 of the transmitted power density
returns from a 1 m^2 target at 1000 m.
```

**What this cell does — The round-trip loss, by hand.**

The geometric verdict on the echo. The loss factor sigma*lambda²/((4 pi)³ R⁴) isolates spreading and target reflection, deliberately leaving transmitter power and antenna gain out. With a 1 m² target at 1000 m and lambda = 0.1224 m it computes to 7.55e-18, or -171.2 dB.

This is pure geometry: only 7.55e-18 of the transmitted power density returns from a 1 m² target at 1000 m. Antenna gain (the G² in the full equation) recovers part of that loss, which is how the channel model later lands on a -40 dB attenuation for the baseline case. The decibel exists to make numbers like this one readable.

## Checkpoint

In your own words, explain why received power falls as R⁴ rather than R².

Then answer this: if the target range doubles, by how many decibels does the received power drop?

## Common mistake

A common mistake is to think the radar equation only matters for long range. In fact it matters at every range — it is the reason the matched filter (Notebook 04) exists. Without the 1 / R⁴ loss, the echo would be strong enough to detect without any processing at all.

Another mistake is to confuse radar cross section with physical size. A stealth aircraft can have a radar cross section millions of times smaller than its physical area, because the shape and materials redirect energy away from the radar.

## Connecting to the channel model

The next notebook (Notebook 03) uses an attenuation of −40 dB for the baseline 1000-metre target. That value comes from the radar equation with plausible transmitter power, antenna gain, and target cross section. The exact number is not important — what matters is understanding that the attenuation is not arbitrary. It is the physical consequence of the signal traveling to the target and back, reflecting off it, and returning.

When you see −40 dB in Notebook 03, you will know it encodes the range, the target, and the geometry — all packed into one number by the radar equation.

## Closing the loop: answers to the opening questions

At the start of this notebook we listed four things you should be able to explain. Here is a direct answer to each one.

### Why radar echoes are so weak

The transmitted energy spreads outward as an expanding sphere (1 / R² loss), only a fraction hits the target (radar cross section), and the reflected energy spreads outward again (another 1 / R² loss). The two spreading losses combine to give 1 / R⁴. A target at 1000 m returns a billion times less power than the radar transmitted.

### What the radar equation says

The radar equation $P_r = P_t G^2 \lambda^2 \sigma / ((4\pi)^3 R^4 L)$ connects the received power to the transmitted power, antenna gain, wavelength, target cross section, range, and system losses. The $R^4$ denominator is the dominant term — it is why range is the hardest challenge in radar.

### Why received power falls as the fourth power of range

The signal makes a round trip. It loses power as 1 / R² on the way out and 1 / R² on the way back. Multiplying the two gives 1 / R⁴. Doubling the range reduces the received power by a factor of 16.

### How the −40 dB attenuation comes from the physics

The −40 dB used in Notebook 03 is the combined effect of the radar equation with plausible system parameters: transmitter power, antenna gain, target cross section, and range. It is not an arbitrary choice — it is the physical outcome of the signal path. The exact value depends on the specific radar and target, but −40 dB is a realistic ballpark for a 1000-metre target.

## Summary

- The radar equation connects transmitted power, antenna gain, wavelength, target cross section, and range to the received power.
- The received power falls as 1 / R⁴ because the signal makes a round trip, spreading on both legs.
- This fourth-power law is why radar echoes are so weak and why signal processing (matched filtering, integration) is essential.
- The −40 dB attenuation in later notebooks comes from the radar equation with plausible parameters — it is physics, not an arbitrary choice.
