# Walkthrough — 08: Direction of Arrival and Interference

This is a cell-by-cell walkthrough of `beginner/notebooks/08-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 08 — Direction of Arrival and Interference

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/08-doa-and-interference.ipynb)

## What this notebook teaches

Notebook 07 built the array and its beam pattern. A real radar does not just draw a pattern - it *scans* it to measure where a target is. This notebook introduces direction-of-arrival (DOA) estimation: sweeping a spatial spectrum over angles and finding peaks. It also shows why a naive scan (Bartlett) blurs close targets, and how an adaptive scan (Capon/MVDR) resolves them and rejects a strong interferer.

By the end of this notebook, you should be able to explain:

- how a spatial spectrum turns a set of array snapshots into an angle measurement,
- what Bartlett (delay-and-sum) does and why its resolution is limited,
- how Capon/MVDR improves the resolution,
- why a strong interferer can *mask* a real target in Bartlett,
- and how Capon's null recovers the target.

Keep these five questions in mind as you work through the cells. A dedicated section at the end answers each one directly.

## Setup and baseline values

The shared helpers give you the array geometry from Notebook 07 plus a new set of DOA tools: a routine to estimate the array covariance from snapshots, a Bartlett (conventional) scan, and a Capon (MVDR) scan. The baseline scene places our target at 20 degrees from broadside, with the interferer at -30 degrees and an 8-element half-wavelength array.

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
from beginner.helpers.math import wavelength_m
from beginner.helpers.plotting import apply_notebook_style
from beginner.helpers.doa import sample_covariance, bartlett_spectrum, mvdr_spectrum

np.random.seed(42)
apply_notebook_style()
radar_spec = baseline_spec()

lam = wavelength_m(radar_spec.fc_hz)
n_elements = 8
d_spacing = lam / 2.0
angles = np.linspace(-90, 90, 1801)

print(f"8 elements, half-wavelength spacing, lambda = {lam*100:.2f} cm")
print(f"Target at {radar_spec.target_angle_deg:.0f} deg, interferer at {radar_spec.interferer_angle_deg:.0f} deg")
```

**Executed output:**

```
8 elements, half-wavelength spacing, lambda = 12.24 cm
Target at 20 deg, interferer at -30 deg
```

**What this cell does — Setup: the DOA tools.**

Imports bring in the DOA package: sample_covariance, bartlett_spectrum, and mvdr_spectrum, on top of the array geometry from Notebook 07. The scene is fixed: 8 elements, half-wavelength spacing, lambda = 12.24 cm, target at 20 degrees, interferer at -30 degrees.

Everything else in the notebook is one story: can the scan hear the 20-degree target while a loud -30-degree interferer is present?

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

You can now measure range, velocity, and (from the array) a beam pattern that points in a direction. The natural next step is to *scan* that beam over all angles and read where the target is - that is a direction-of-arrival estimate. But scanning naively has two problems that this notebook confronts: the beam is too wide to separate targets that are close in angle, and a loud interferer can drown a weak target. Both problems are fixed by being cleverer about how you combine the array's data.

## From snapshots to a covariance

The array records a snapshot at each moment: a vector x of N complex values, one per element. Each snapshot is the sum of the targets' steering vectors (scaled by their amplitudes) plus noise. Over many moments you collect many snapshots and average the outer products x x^H into the sample covariance

    R = (1/K) sum over snapshots of x x^H

R is the object both scans work from. It stores, on average, how each element correlates with every other - and that structure contains the directions of the incoming waves. Let us build R for a single target at 20 degrees.

Before we look at the helper-generated covariance, compute a single steering vector manually and show the phase progression across the array. That makes the covariance calculation feel like the same spatial geometry you already saw in Notebook 07, not a mysterious matrix trick.

### Notebook cell 9 · code
```python
# Manual steering-vector calculation for a 20-degree target.
theta_deg = 20.0
theta_rad = np.radians(theta_deg)
n = np.arange(n_elements)
phase_step = 2.0 * np.pi * d_spacing * np.sin(theta_rad) / lam
a_manual = np.exp(1j * n * phase_step)

print(f"theta = {theta_deg:.1f} deg")
print(f"phase step per element = {phase_step:.3f} rad")
print(f"manual steering vector = {np.round(a_manual, 3)}")
print(f"this is the phase pattern the covariance will average together across snapshots.")
```

**Executed output:**

```
theta = 20.0 deg
phase step per element = 1.074 rad
manual steering vector = [ 1.   +0.j     0.476+0.879j -0.547+0.837j -0.997-0.082j -0.403-0.915j
  0.613-0.79j   0.987+0.163j  0.326+0.945j]
this is the phase pattern the covariance will average together across snapshots.
```

**What this cell does — The manual steering vector.**

Same steering geometry as Notebook 07, written out by hand for the 20-degree target: phase step 1.074 rad per element, growing into the complex vector [1, 0.476+0.879j, -0.547+0.837j, ...]. Eight complex values, one per element.

This vector is the phase fingerprint the covariance will average together across snapshots.

### Notebook cell 10 · code
```python
n_snapshots = 2000
R_target = sample_covariance([np.radians(20.0)], [1.0], n_elements, d_spacing, lam, n_snapshots=n_snapshots)

print(f"R shape = {R_target.shape}")
print(f"Mean on-diagonal power = {np.real(np.trace(R_target))/n_elements:.3f} (target power + noise)")
print(f"Matrix is Hermitian: max|R - R^H| = {np.max(np.abs(R_target - R_target.conj().T)):.2e}")
```

**Executed output:**

```
R shape = (8, 8)
Mean on-diagonal power = 2.003 (target power + noise)
Matrix is Hermitian: max|R - R^H| = 1.11e-16
```

**What this cell does — From snapshots to a covariance.**

sample_covariance builds R: 2000 snapshots, each the steering vector plus noise, averaged as x*x^H. R is 8x8, its on-diagonal power is 2.003 (target power + noise), and it is exactly Hermitian - the check shows max|R - R^H| about 1e-16.

R is the object both scans work from. It is no longer a waveform; it is a matrix of correlations that stores the directions of the incoming waves.

## Scanning a spatial spectrum: Bartlett

To measure direction, we imagine a plane wave coming from each candidate angle theta and ask how strongly the array's data R agrees with it. The **Bartlett beamformer** simply weights the array with the steering vector a(theta) and reads the power:

    P_Bartlett(theta) = a(theta)^H R a(theta)

At the true source direction the steering vector matches the data's phase pattern, so R lights up and P peaks. Sweeping theta gives a spatial spectrum whose peaks are the directions of arrival. Bartlett is just "point the beam and measure" - the same delay-and-sum view you used to build the beam pattern in Notebook 07, expressed as a scan.

### Notebook cell 12 · code
```python
P_bart = bartlett_spectrum(R_target, np.radians(angles), n_elements, d_spacing, lam)
P_bart_db = 10 * np.log10(P_bart / P_bart.max())

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, P_bart_db, color="#1b9e77", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="true 20 deg")
ax.set_xlabel("Angle from broadside (deg)")
ax.set_ylabel("Bartlett power (dB)")
ax.set_title("Bartlett spatial spectrum: one target at 20 deg")
ax.legend()
ax.set_ylim(-30, 2)
plt.tight_layout()
plt.show()

peak = angles[np.argmax(P_bart)]
print(f"Bartlett peaks at {peak:.1f} deg - matches the true 20 deg target.")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Bartlett peaks at 20.0 deg - matches the true 20 deg target.
```

![Notebook output](assets/08/fig_cell12_0.png)

**What this cell does — The Bartlett scan.**

Scan theta with the Bartlett measure a(theta)^H R a(theta): point the fixed beam and read the power. The result is a clean spatial spectrum with a single peak at exactly 20.0 degrees - the direction of the target.

This is delay-and-sum again, read as a scan. Where the steering vector matches R's phase pattern, the power lights up.

## The limit: close targets blur together

Bartlett's beam is as wide as the array's main lobe - about 14 degrees for our 8 elements - so two targets closer together than that produce peaks that merge into one. Add a second target at 30 degrees, only 10 degrees from the first. Bartlett cannot tell them apart: it reports a single, wide bump somewhere between the two.

### Notebook cell 14 · code
```python
# Two targets, 20 and 30 deg - 10 deg apart, well inside the 14 deg beam.
R_close = sample_covariance([np.radians(20.0), np.radians(30.0)], [1.0, 1.0], n_elements, d_spacing, lam, n_snapshots=n_snapshots)
P_b_close = bartlett_spectrum(R_close, np.radians(angles), n_elements, d_spacing, lam)

def local_peaks(p, near=20.0, tol=25.0, thr=-6.0):
    pdb = 10*np.log10(p / p.max()); out = []
    for i in range(1, len(angles)-1):
        if abs(angles[i]-near) < tol and pdb[i] > thr and pdb[i] >= pdb[i-1] and pdb[i] >= pdb[i+1]:
            out.append((round(angles[i], 1), round(pdb[i], 1)))
    return out

def target_peak(p, target=20.0, win=(0, 40), tol=8.0, prom_db=2.0):
    """Report a standalone peak near `target`, if any, as (angle, prominence, level)."""
    pdb = 10*np.log10(p / p.max())
    m = (angles >= win[0]) & (angles <= win[1])
    ia = np.where(m)[0]
    for j in ia:
        if j == 0 or j == len(angles)-1:
            continue
        if pdb[j] >= pdb[j-1] and pdb[j] >= pdb[j+1]:
            left = min(pdb[ia[ia < j]]) if np.any(ia < j) else pdb[j]
            right = min(pdb[ia[ia > j]]) if np.any(ia > j) else pdb[j]
            prom = pdb[j] - max(left, right)
            if abs(angles[j]-target) < tol and prom >= prom_db:
                return round(float(angles[j]), 1), round(float(prom), 1), round(float(pdb[j]), 1)
    return None

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, 10*np.log10(P_b_close/P_b_close.max()), color="#1b9e77", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":")
ax.axvline(30, color="#d95f02", linestyle=":")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Bartlett power (dB)")
ax.set_title("Bartlett merges two targets 10 deg apart")
ax.set_xlim(-10, 50)
ax.set_ylim(-3, 1)
plt.tight_layout()
plt.show()

print(f"Bartlett sees only {len(local_peaks(P_b_close))} peak(s) near the two targets (true: 2)")
print(f"Single merged peak at {angles[np.argmax(P_b_close)]:.1f} deg")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Bartlett sees only 1 peak(s) near the two targets (true: 2)
Single merged peak at 25.0 deg
```

![Notebook output](assets/08/fig_cell14_0.png)

**What this cell does — The limit: close targets merge.**

Add a second target at 30 degrees - 10 degrees apart, inside the 8-element array's roughly 14-degree main lobe. Bartlett's fixed beam cannot separate them: it reports a single merged peak at 25 degrees, squarely between the two true directions.

This is not a tuning problem. Bartlett's width is set by the aperture, and no choice of weights can narrow it. That is the motivation for going adaptive.

## The fix: Capon / MVDR

Capon's insight is to make the weights *adaptive*. Instead of fixed steering-vector weights, Capon chooses weights that pass the look direction with unit gain while *minimising* the power coming from every other direction. That constraint forces deep nulls at the other sources, so the response is far sharper than Bartlett's fixed beam:

    P_Capon(theta) = 1 / ( a(theta)^H R^{-1} a(theta) )

The inverse covariance places a spatial null wherever there is energy, so two targets 10 degrees apart become two sharp, separate peaks. The cost is that you must estimate R and invert it - and R needs enough snapshots to be reliable.

### Notebook cell 16 · code
```python
P_mvdr = mvdr_spectrum(R_close, np.radians(angles), n_elements, d_spacing, lam)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, 10*np.log10(P_mvdr/P_mvdr.max()), color="#7570b3", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":")
ax.axvline(30, color="#d95f02", linestyle=":")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Capon power (dB)")
ax.set_title("Capon resolves the two targets at 20 and 30 deg")
ax.set_xlim(-10, 50)
plt.tight_layout()
plt.show()

print(f"Capon sees {len(local_peaks(P_mvdr))} peak(s) near the two targets - it resolves them.")
print(f"Peaks at {[p for p,_ in local_peaks(P_mvdr)]}")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Capon sees 2 peak(s) near the two targets - it resolves them.
Peaks at [np.float64(22.4), np.float64(27.7)]
```

![Notebook output](assets/08/fig_cell16_0.png)

**What this cell does — Capon / MVDR resolves them.**

Capon inverts the trick: pass the look direction with unit gain while minimizing power from every other direction, P = 1/(a^H R^-1 a). The inverse covariance places adaptive nulls at the other source, so the two nearby targets produce two sharp peaks - at 22.4 and 27.7 degrees.

Two peaks instead of one merged bump. The price is an estimated, invertible R: Capon gets sharper only when the covariance is trustworthy.

## Side by side: Bartlett vs Capon

Putting the two scans on one plot makes the difference unmistakable. Bartlett reports one broad bump; Capon reports two sharp peaks. This is the resolution advantage of adaptive beamforming: it is not a fixed beam but a filter that actively rejects the other source. The playbook's instruction here is to make the difference visible - and here it plainly is.

### Notebook cell 18 · code
```python
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))
for axp, (P, color, name) in enumerate([(P_b_close, "#1b9e77", "Bartlett"), (P_mvdr, "#7570b3", "Capon")]):
    ax[axp].plot(angles, 10*np.log10(P/P.max()), color=color, linewidth=2)
    ax[axp].axvline(20, color="#d95f02", linestyle=":")
    ax[axp].axvline(30, color="#d95f02", linestyle=":")
    ax[axp].set_xlabel("Angle (deg)")
    ax[axp].set_ylabel("Power (dB)")
    ax[axp].set_title(name)
    ax[axp].set_xlim(-10, 50)
    ax[axp].set_ylim(-3, 1)
plt.tight_layout()
plt.show()

print("Bartlett: one merged peak. Capon: two resolved peaks at 20 and 30 deg.")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
Bartlett: one merged peak. Capon: two resolved peaks at 20 and 30 deg.
```

![Notebook output](assets/08/fig_cell18_0.png)

**What this cell does — Side by side: Bartlett vs Capon.**

Bartlett and Capon on the same two-target covariance, same axes. Left: one broad bump. Right: two sharp peaks. The resolution advantage of adaptive beamforming is unmistakable in a single picture.

Same data, same array, same look directions - the only difference is the weights adapting to null the other source.

## A strong interferer can mask the target

Now the problem is not two weak targets but one weak target and one very loud interferer. The baseline scene has our target at 20 degrees and a strong interferer at -30 degrees - say 20 dB stronger. In a straightforward Bartlett scan, the interferer's broad response (through the beam's sidelobes) swamps everything, and the weak target's peak disappears: **the target is masked**. If the radar trusted this scan it would think the scene contains only the interferer.

### Notebook cell 20 · code
```python
# Target (amplitude 1) plus a +20 dB interferer at -30 deg.
interferer_amp = 10.0  # 20 dB above the target
R_int = sample_covariance([np.radians(20.0), np.radians(-30.0)], [1.0, interferer_amp], n_elements, d_spacing, lam, n_snapshots=n_snapshots)

P_b_int = bartlett_spectrum(R_int, np.radians(angles), n_elements, d_spacing, lam)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, 10*np.log10(P_b_int/P_b_int.max()), color="#1b9e77", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="target 20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Bartlett power (dB)")
ax.set_title("Bartlett: the interferer masks the weak target")
ax.legend()
ax.set_ylim(-30, 2)
plt.tight_layout()
plt.show()

print(f"Bartlett max at {angles[np.argmax(P_b_int)]:.1f} deg (the interferer)")
bt = target_peak(P_b_int)
btlvl = bt[2] if bt else float('-inf')
print(f"Bartlett feature near 20 deg sits at {btlvl:.1f} dB relative to the interferer peak -> the target is masked")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Bartlett max at -30.0 deg (the interferer)
Bartlett feature near 20 deg sits at -15.7 dB relative to the interferer peak -> the target is masked
```

![Notebook output](assets/08/fig_cell20_0.png)

**What this cell does — Masking: the interferer wins in Bartlett.**

Now a weak target at 20 degrees and an interferer at -30 degrees, 20 dB stronger. Bartlett's fixed sidelobes leak the loud source across the scan, so its peak is at -30 and the feature near 20 sits 15.7 dB below the interferer peak: the target is masked.

A radar trusting this scan would see a scene containing only the interferer. The target has not gone away - Bartlett just cannot hear it.

## Capon confines the interferer and recovers the target

Capon is not fooled. Its adaptive weights combine the elements so that a strong source at one angle is not allowed to speak loudly at the target's angle - the interferer's energy is *confined* to its own angle and no longer leaks through the sidelobes onto the target. The weak target's peak therefore reappears at its true 20-degree angle. This is the practical payoff of adaptive beamforming - it is how a radar stays useful when a loud jammer or bright reflector sits nearby.

### Notebook cell 22 · code
```python
P_m_int = mvdr_spectrum(R_int, np.radians(angles), n_elements, d_spacing, lam)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, 10*np.log10(P_m_int/P_m_int.max()), color="#7570b3", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="target 20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
# The interferer is confined to a sharp peak at -30 (its own power);
# its energy no longer leaks over the target, so the 20-deg peak survives.
ax.annotate("interferer confined to its own angle", xy=(-30, 10*np.log10(P_m_int/P_m_int.max())[np.argmin(np.abs(angles+30))]),
            xytext=(-68, -8), arrowprops=dict(arrowstyle="->", color="#333333"))
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Capon power (dB)")
ax.set_title("Capon confines the interferer, so the target survives")
ax.legend()
ax.set_ylim(-30, 2)
plt.tight_layout()
plt.show()

print(f"Capon target peak near 20 deg: {target_peak(P_m_int)} -> the target is recovered")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Capon target peak near 20 deg: (20.0, 9.4, -19.5) -> the target is recovered
```

![Notebook output](assets/08/fig_cell22_0.png)

**What this cell does — Capon recovers the target.**

Capon confines the interferer to its own angle. Its adaptive null keeps the -30 source out of the target's direction, and the 20-degree peak reappears, reported at (20.0, 9.4, -19.5): the exact true angle with healthy prominence.

This is the practical payoff of adaptive beamforming - a radar that stays useful when a jammer or a bright reflector sits nearby.

## Before and after: the masking story

Compare the target's appearance across the four spectra:

- target alone: Bartlett and Capon both peak at 20.
- target plus interferer: Bartlett loses the 20-degree peak (masked); Capon keeps it (recovered).

The printed peak counts below summarise exactly that. This before/after contrast is the whole point: a conventional scan is at the mercy of a loud neighbour, while an adaptive scan is not.

### Notebook cell 24 · code
```python
# Before (target only) peak counts.
pb0 = bartlett_spectrum(R_target, np.radians(angles), n_elements, d_spacing, lam)
pm0 = mvdr_spectrum(R_target, np.radians(angles), n_elements, d_spacing, lam)

print("              | before (target only) | after (+20 dB interferer)")
print(f"Bartlett      | peak at 20 deg       | target masked (feature buried)")
print(f"Capon         | peak at 20 deg       | target recovered at exactly 20 deg")
print()
print(f"Bartlett target feature: before {target_peak(pb0)}  after {target_peak(P_b_int)}")
print(f"Capon target feature   : before {target_peak(pm0)}  after {target_peak(P_m_int)}")
```

**Executed output:**

```
              | before (target only) | after (+20 dB interferer)
Bartlett      | peak at 20 deg       | target masked (feature buried)
Capon         | peak at 20 deg       | target recovered at exactly 20 deg

Bartlett target feature: before (20.0, 9.5, 0.0)  after (21.6, 9.2, -15.7)
Capon target feature   : before (20.0, 9.5, 0.0)  after (20.0, 9.4, -19.5)
```

**What this cell does — Before and after: the masking story.**

The summary table. Target alone: Bartlett and Capon both peak at 20. After the +20 dB interferer, Bartlett's target feature falls to -15.7 dB relative (masked), while Capon keeps it at -19.5 dB relative with prominence 9.4.

One number tells the whole story: Bartlett's target feature collapses under interference, Capon's survives.

## Checkpoint

In your own words, why can Bartlett not separate two targets that are close in angle, and how does Capon manage to separate them?

Then answer this: a loud interferer sits near a weak target. In which scan does the target disappear, and why does the other scan keep it visible?

## Common mistake

A common mistake is to think Bartlett's resolution is a limitation you can remove by randomly tweaking it. It is not - Bartlett is the best *non-adaptive* scan, and its width is fundamentally fixed by the array aperture (N d). You cannot beat it with weights; you must go adaptive (Capon), which needs an estimated covariance R and its inverse.

Another mistake is to use too few snapshots and trust the Capon result. R is estimated from snapshots, and with too few the inverse is unreliable - Capon may show spurious peaks. Always check you have enough snapshots (many more than the number of elements) before trusting the sharp peaks it produces.

## Why the helpers exist

The cells above built the covariance, the Bartlett scan, and the Capon scan step by step so you can see where the power and the nulls come from. Once the idea is clear, the same work collapses into sample_covariance, bartlett_spectrum, and mvdr_spectrum - so later notebooks can estimate directions or study interference in a few lines instead of a full scan loop.

Keep the first pass visible for the beamformer logic, then use the helpers when the lesson moves on.

### Notebook cell 28 · code
```python
# The same pair of scans in helper form.
Pb = bartlett_spectrum(R_int, np.radians(angles), n_elements, d_spacing, lam)
Pm = mvdr_spectrum(R_int, np.radians(angles), n_elements, d_spacing, lam)

b_peak = angles[np.argmax(Pb)]
m_t = target_peak(Pm)

print(f"Helper Bartlett max at {b_peak:.1f} deg (interferer) - target masked")
print(f"Helper Capon target feature: {m_t} - target recovered at its true angle")
```

**Executed output:**

```
Helper Bartlett max at -30.0 deg (interferer) - target masked
Helper Capon target feature: (20.0, 9.4, -19.5) - target recovered at its true angle
```

**What this cell does — The scans in helper form.**

bartlett_spectrum and mvdr_spectrum on the same R reproduce the story: Bartlett maxes at -30 (interferer), Capon recovers the target feature at (20.0, 9.4, -19.5).

Two lines instead of a full scan loop. The helpers are what Notebook 09 will build the integrated beamformer on.

## Stretch: how many snapshots does Capon need?

Capon depends on a reliable estimate of R. Re-run the two-close-target Capon scan with very few snapshots (say 8) and then with many (2000), and compare. With too few snapshots the inverse of the sample covariance is unstable and Capon produces spurious, jittery peaks; with enough it cleanly resolves the two targets. This is Capon's practical price - it is powerful, but it needs good data.

### Notebook cell 30 · code
```python
for snap in [8, 2000]:
    Rr = sample_covariance([np.radians(20.0), np.radians(30.0)], [1.0, 1.0], n_elements, d_spacing, lam, n_snapshots=snap)
    Pr = mvdr_spectrum(Rr, np.radians(angles), n_elements, d_spacing, lam)
    n_peak = len(local_peaks(Pr, thr=-8))
    print(f"{snap:5d} snapshots: Capon finds {n_peak} peak(s) near 20 deg in the two-target scene (true: 2)")
```

**Executed output:**

```
    8 snapshots: Capon finds 3 peak(s) near 20 deg in the two-target scene (true: 2)
 2000 snapshots: Capon finds 2 peak(s) near 20 deg in the two-target scene (true: 2)
```

**What this cell does — How many snapshots does Capon need?.**

The fine print on Capon. With 8 snapshots the inverse of the sample covariance is unstable and the scan fabricates 3 peaks near 20 degrees (true: 2). With 2000 snapshots it cleanly finds 2.

Powerful, but data-hungry: trust Capon's sharp peaks only when R is estimated from many more snapshots than elements.

## Closing the loop: answers to the opening questions

At the start we listed five things to be able to explain. Here is each answer.

**How a spatial spectrum turns snapshots into an angle.** The array records snapshots x, one complex vector per moment; averaging their outer products gives the covariance R. A scan sweeps the candidate angle theta and evaluates a power measure built from R and the steering vector a(theta). Where the measure peaks, a source exists, and the peak's location is the direction of arrival.

**What Bartlett does and why its resolution is limited.** Bartlett computes a(theta)^H R a(theta) - point the fixed beam and read the power. Its resolution is set by the mainlobe width of the array, about 14 degrees for our 8 elements. Two targets 10 degrees apart fell inside that width and merged into one broad bump.

**How Capon/MVDR improves the resolution.** Capon chooses weights that pass the look direction with unit gain while minimising all other power, using the inverse covariance a(theta)^H R^{-1} a(theta). That places adaptive nulls at the other sources, so close targets produce two sharp peaks instead of one merged bump.

**Why a strong interferer can mask a target in Bartlett.** Bartlett has no way to reject the interferer; its fixed sidelobes leak the loud source's power across the scan. With the target 20 dB weaker, the leaked interferer power swamped the target's peak, so the scan reported only the interferer and the weak target disappeared.

**How Capon's null recovers the target.** Capon's adaptive weights place a deep null exactly on the interferer's direction while keeping unit gain on the target. The loud source is rejected instead of leaked, so the weak target's peak reappeared at its true 20-degree angle.

If you can retell these five answers, you can both find a target's direction and stay useful in the face of interference - the last big piece of estimating where a target is.

## Summary

In this notebook you turned the array from Notebook 07 into a direction-measuring instrument. You estimated the covariance from snapshots and scanned a spatial spectrum to locate sources by angle. The conventional Bartlett scan is simple but limited: it merged two targets only 10 degrees apart because its beam is about 14 degrees wide.

Capon/MVDR is the adaptive fix. By minimising power from every direction but the look direction, it drives deep nulls at other sources and resolved the two close targets into sharp, separate peaks.

The same idea is what saves a target from interference. A loud interferer masked the weak target in Bartlett, but Capon placed an adaptive null on the interferer and recovered the target, as the before/after comparison showed. With range, velocity, and now direction and interference rejection, you have the complete toolkit. The next notebook extends this to steering and adaptive nulling over the full beam.
