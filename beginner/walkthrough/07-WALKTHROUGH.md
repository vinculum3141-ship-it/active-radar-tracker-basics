# Walkthrough — 07: Array Geometry and Beam Patterns

This is a cell-by-cell walkthrough of `beginner/notebooks/07-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 07 — Array Geometry and Beam Patterns

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/07-array-geometry-beam-patterns.ipynb)

## What this notebook teaches

So far you have located a target in *range* and *velocity*. A single antenna cannot tell you where along a circle of constant range the target is - it has no sense of direction. A radar with many antennas arranged in a line - a **uniform linear array (ULA)** - measures *angle*, and the collection of antennas shapes the direction the radar listens to.

By the end of this notebook, you should be able to explain:

- how a line of antennas turns a time delay between elements into an angle,
- what the element spacing is and why half a wavelength is the usual choice,
- how the phase stepping between elements forms the **steering vector**,
- why the **array factor** (beam pattern) has a main lobe and sidelobes, and
- when and why **grating lobes** appear.

Keep these five questions in mind as you work through the cells. A dedicated section at the end answers each one directly.

## Setup and baseline values

The shared helpers give you the baseline radar parameters. This notebook introduces a single new object - a line of antenna elements - and the geometry that turns their shared phase into a direction measurement.

Our baseline radar uses the same 2.45 GHz carrier you have used all along, so the wavelength is about 12.2 cm. The baseline scene places the target at an angle of 20 degrees from broadside, which we will revisit throughout.

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

np.random.seed(42)
apply_notebook_style()
radar_spec = baseline_spec()

lam = wavelength_m(radar_spec.fc_hz)
print(f"Carrier wavelength = {lam*100:.2f} cm (fc = {radar_spec.fc_hz/1e9:.2f} GHz)")
print(f"Baseline target angle = {radar_spec.target_angle_deg:.0f} deg from broadside")

lam
```

**Executed output:**

```
Carrier wavelength = 12.24 cm (fc = 2.45 GHz)
Baseline target angle = 20 deg from broadside
0.12236426857142857
```

**What this cell does — Setup: wavelength and baseline angle.**

Imports the baseline spec and the wavelength helper. The 2.45 GHz carrier gives a 12.24 cm wavelength, and the baseline target sits at 20 degrees from broadside. The trailing lam also displays the raw wavelength in the output.

Everything in the beam story hangs on those two numbers: lambda = 12.24 cm and theta = 20 degrees.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

You can already say *how far* a target is (range) and *how fast* it moves (velocity). The missing coordinate is direction: a single antenna is a point, so the echo tells you the target lies somewhere on a circle of constant range, but not *where* on that circle.

An array of antennas changes that. If the same echo arrives at several elements, it reaches each one at a slightly different time (and phase), because the path length differs by a fraction of a wavelength. That path difference encodes the angle. This notebook builds the geometry and the pattern; the next notebook turns it into an actual direction measurement and deals with interference.

## Array geometry: a line of elements

A uniform linear array places N identical elements along a line, spaced a fixed distance d apart. We put the elements along the x-axis with the first at the origin. The target's direction is described by the angle theta measured from **broadside** - the direction perpendicular to the line of the array (so broadside is theta = 0).

A wave from a target at angle theta has to travel a little farther to reach each successive element. Look at one gap: the extra path length from one element to the next is

    d * sin(theta)

because the wavefront crosses the gap along the direction of arrival. That small extra distance is exactly what the array is built to exploit.

### Notebook cell 9 · code
```python
n_elements = 8
d_spacing = lam / 2.0        # half-wavelength spacing

# Draw the elements along the x-axis.
xs = np.arange(n_elements) * d_spacing
fig, ax = plt.subplots(figsize=(9, 2.5))
ax.plot(xs, np.zeros_like(xs), 'o', color="#1b9e77", markersize=10)
ax.set_yticks([])
ax.set_xlabel("Position along array (m)")
ax.set_title(f"{n_elements} elements spaced {d_spacing*100:.2f} cm (half a wavelength)")
ax.axhline(0, color="#999999", linewidth=0.8)
# Mark the first gap so the sin(theta) path difference is easy to see.
ax.annotate("", xy=(d_spacing, 0), xytext=(0, 0),
            arrowprops=dict(arrowstyle="<->", color="#d95f02"))
plt.tight_layout()
plt.show()

print(f"Wavelength  = {lam*100:.2f} cm")
print(f"Element gap = {d_spacing*100:.2f} cm = lambda/2")
print(f"Maximum extra path across one gap = d * sin(90 deg) = {d_spacing*100:.2f} cm")
```

**Executed output:**

```
<Figure size 900x250 with 1 Axes>
Wavelength  = 12.24 cm
Element gap = 6.12 cm = lambda/2
Maximum extra path across one gap = d * sin(90 deg) = 6.12 cm
```

![Notebook output](assets/07/fig_cell9_0.png)

**What this cell does — Geometry: a line of 8 elements.**

An 8-element uniform linear array drawn along the x-axis with half-wavelength spacing: d = 6.12 cm. The orange brace marks one gap to emphasize the path difference d*sin(theta) between neighbouring elements.

Maximum extra path across a single gap is d*sin(90 deg) = 6.12 cm = half a wavelength, and that path difference is the source of phase between elements.

## Element spacing: why half a wavelength

The spacing d is not free - it trades two things.

A **large d** makes the phase difference between elements grow quickly with angle, so the beam is *narrower* (better resolution). But the phase wraps around every full wavelength, and if the wrapped phase is not unique across the visible range (+-90 degrees), the array cannot tell one direction from another and spurious **grating lobes** appear - whole extra copies of the main beam pointing the wrong way.

A **small d** is unambiguous but gives a wider beam. The standard compromise is half a wavelength, d = lambda/2. Then the phase step per element is

    Delta_phi = (2 pi d / lambda) * sin(theta) = pi * sin(theta)

which stays within +-pi over the whole visible range, so there is exactly one main lobe and no grating lobes. We will see what happens when d grows past this later.

Before we use the array helper functions, let us compute the phase step and the angle-dependent path difference explicitly for the baseline target at 20 degrees.

### Notebook cell 11 · code
```python
# Manual geometry calculation for the 20-degree target.
theta_deg = 20.0
theta_rad = np.radians(theta_deg)
d_spacing = lam / 2.0
phase_step = 2.0 * np.pi * d_spacing * np.sin(theta_rad) / lam
extra_path_per_element = d_spacing * np.sin(theta_rad)

print(f"theta = {theta_deg:.1f} deg -> {theta_rad:.3f} rad")
print(f"element spacing d = {d_spacing:.4f} m")
print(f"extra path per element = {extra_path_per_element:.4f} m")
print(f"phase step per element = {phase_step:.3f} rad = {np.degrees(phase_step):.1f} deg")
print(f"This is the phase advance that creates the array's steering pattern.")
```

**Executed output:**

```
theta = 20.0 deg -> 0.349 rad
element spacing d = 0.0612 m
extra path per element = 0.0209 m
phase step per element = 1.074 rad = 61.6 deg
This is the phase advance that creates the array's steering pattern.
```

**What this cell does — The phase step, by hand.**

Manual geometry for the 20-degree target: extra path per element = d*sin(theta) = 2.09 cm (0.171 wavelengths), which becomes a phase step of 2*pi*d*sin(theta)/lambda = 1.074 rad = 61.6 degrees. That per-element rotation is what the array is built to exploit.

One number to remember: 61.6 degrees between neighbours. The rest of the notebook spreads this step across the 8 elements.

The phase offset between elements for the baseline 20-degree target:

    Delta_phi = pi * sin(20 deg) = pi * 0.342 = 1.07 rad = 61.6 deg

### Notebook cell 13 · code
```python
from beginner.helpers.array import inter_element_phase_rad

ang_deg = radar_spec.target_angle_deg   # 20 degrees
ang_rad = np.radians(ang_deg)
dphi = inter_element_phase_rad(ang_rad, d_spacing, lam)

print(f"Target at {ang_deg:.0f} deg from broadside (half-wavelength spacing)")
print(f"Inter-element phase step = {dphi:.3f} rad = {np.degrees(dphi):.1f} deg")

# Extra path length across one gap, in cm.
extra = d_spacing * np.sin(ang_rad)
print(f"Extra path per gap = {extra*100:.2f} cm = {(extra/lam):.3f} wavelengths")
```

**Executed output:**

```
Target at 20 deg from broadside (half-wavelength spacing)
Inter-element phase step = 1.074 rad = 61.6 deg
Extra path per gap = 2.09 cm = 0.171 wavelengths
```

**What this cell does — The same step from the helper.**

inter_element_phase_rad confirms the by-hand number: 61.6 degrees, or 0.171 wavelengths of extra path per gap.

Boring agreement is the point: the helper exists so later notebooks compute this in one line.

## The steering vector

The phase offset builds up as you move along the array. Element 0 has phase 0, element 1 has phase Delta_phi, element 2 has 2*Delta_phi, and so on. Collecting the complex amplitude at each element gives the **steering vector**:

    a(theta) = [1, e^{j Delta_phi}, e^{j 2 Delta_phi}, ..., e^{j (N-1) Delta_phi}]

It is a complex vector - one value per element, just like the complex echo values you handled in the Doppler notebooks. It describes the pattern of phase the echo imprints on the array when it arrives from direction theta.

### Notebook cell 15 · code
```python
from beginner.helpers.array import steering_vector

a = steering_vector(ang_rad, n_elements, d_spacing, lam)
elem = np.arange(n_elements)

fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))
ax[0].plot(elem, a.real, 'o-', color="#1b9e77", label="Real part")
ax[0].plot(elem, a.imag, 's-', color="#d95f02", label="Imaginary part")
ax[0].set_xlabel("Element index")
ax[0].set_ylabel("Steering vector value")
ax[0].set_title(f"Steering vector for theta = {ang_deg:.0f} deg")
ax[0].legend()

ph = np.angle(a)
ax[1].plot(elem, np.degrees(ph), 'o-', color="#7570b3")
ax[1].set_xlabel("Element index")
ax[1].set_ylabel("Phase (deg)")
ax[1].set_title("Phase wraps steadily by the inter-element step")
plt.tight_layout()
plt.show()

print(f"Phase per element increments by about {np.degrees(dphi):.1f} deg")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
Phase per element increments by about 61.6 deg
```

![Notebook output](assets/07/fig_cell15_0.png)

**What this cell does — The steering vector.**

The steering vector stacks one complex amplitude per element, each phase stepping by 61.6 degrees: [1, e^j1.07, e^j2.14, ...]. The right panel shows the phase wrapping steadily across the 8 elements.

This is the fingerprint a wave from 20 degrees imprints on the array. The absolute phase means nothing; only the step between neighbours matters.

## Combining the elements: the array factor

To listen in a direction, the radar combines the elements coherently - it multiplies the echo at each element by a weight and sums. For an unsteered array the weights are all 1, and the response as a function of direction is the **array factor**:

    AF(theta) = sum over n of w_n e^{j n k d sin(theta)}

where k = 2 pi / lambda. This is a sum of unit vectors whose phases rotate as theta moves off broadside. At theta = 0 every term is +1 and they add to N: a strong main lobe. Away from broadside the phases spread out and partially cancel, forming the pattern's sidelobes. Plotting |AF| over all angles gives the textbook beam pattern.

### Notebook cell 17 · code
```python
from beginner.helpers.array import array_factor, first_null_angle_deg

thetas = np.linspace(-90, 90, 1801)
AF = array_factor(np.radians(thetas), n_elements, d_spacing, lam)
mag = np.abs(AF)
mag_n = mag / mag.max()

# Peak sidelobe: ignore the main lobe by masking out its first-null span.
null_deg = first_null_angle_deg(n_elements, d_spacing, lam)
mask = np.abs(thetas) > (null_deg + 1.0)
sidelobe_db = 20 * np.log10(mag_n[mask].max())

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(thetas, mag_n, color="#1b9e77", linewidth=2)
ax.axvline(0, color="#999999", linestyle=":")
ax.set_xlabel("Angle from broadside (deg)")
ax.set_ylabel("Normalized |array factor|")
ax.set_title(f"Beam pattern: {n_elements} elements, half-wavelength spacing")
plt.tight_layout()
plt.show()

print(f"Main lobe at 0 deg (broadside), peak value = {mag_n.max():.3f}")
print(f"First sidelobe beside the main lobe sits about {sidelobe_db:.1f} dB below it")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Main lobe at 0 deg (broadside), peak value = 1.000
First sidelobe beside the main lobe sits about -12.8 dB below it
```

![Notebook output](assets/07/fig_cell17_0.png)

**What this cell does — The array factor and beam pattern.**

Combine the elements with weights and sweep the response over angle: the array factor. At broadside all phases align and the sum peaks at 8 (N); away from it the phases spread and partially cancel, leaving the main lobe and sidelobes. The first sidelobe sits about 12.8 dB below the peak.

This is the textbook beam pattern: one main lobe, decaying sidelobes, and - for half-wavelength spacing - no false copies.

## Reading the pattern: nulls and beamwidth

The main lobe is the response you want - the directions the array accepts most strongly. The first null of a uniform array falls at

    sin(theta_null) = lambda / (N d)

With N = 8 and d = lambda/2, that is sin(theta_null) = 1/4, so the first null sits at about 14.5 degrees and the beam is about 29 degrees wide between the two first nulls. More elements, or wider spacing, both narrow the beam - a bigger array resolves angles more finely.

### Notebook cell 19 · code
```python
from beginner.helpers.array import first_null_angle_deg

null_deg = first_null_angle_deg(n_elements, d_spacing, lam)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(thetas, mag_n, color="#1b9e77", linewidth=2)
ax.axvline(null_deg, color="#d95f02", linestyle="--", label=f"first null +{null_deg:.1f} deg")
ax.axvline(-null_deg, color="#d95f02", linestyle="--", label=f"first null -{null_deg:.1f} deg")
ax.set_xlabel("Angle from broadside (deg)")
ax.set_ylabel("Normalized |array factor|")
ax.set_title("First nulls bracket the main lobe")
ax.legend()
plt.tight_layout()
plt.show()

print(f"First null at {null_deg:.1f} deg  ->  beam is about {2*null_deg:.1f} deg wide between nulls")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
First null at 14.5 deg  ->  beam is about 29.0 deg wide between nulls
```

![Notebook output](assets/07/fig_cell19_0.png)

**What this cell does — Reading the pattern: nulls and beamwidth.**

The first null of an 8-element, half-wavelength array falls at sin(theta_null) = lambda/(N*d) = 1/4, so 14.5 degrees. The beam is therefore about 29 degrees wide between its first two nulls.

A bigger array (more N) or wider spacing both narrow the beam - the aperture decides angular resolution.

## Steering the beam

An unsteered array listens at broadside. To listen at any other angle, you shift each element's phase to *undo* the delay the wave picked up travelling across the array - you multiply element n by e^{-j n Delta_phi} for the direction you want. The weights become a steering vector, and the beam's main lobe moves to that angle.

This is exactly how the baseline 20-degree target is found: the radar scans theta, and where the beam (with scanning-steering weights applied) puts its main lobe, that is where the target is. The next notebook turns this scanning into a measured angle.

Here we steer the same 8-element array to 20 degrees and show the main lobe follow:

### Notebook cell 22 · code
```python
# Steer by applying steering-vector weights (conjugate phases).
def steered_mag(thetas_deg, steer_deg):
    w = steering_vector(np.radians(steer_deg), n_elements, d_spacing, lam).conj()
    af = array_factor(np.radians(thetas_deg), n_elements, d_spacing, lam, weights=w)
    return np.abs(af) / np.abs(af).max()

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(thetas, steered_mag(thetas, 0.0), color="#1b9e77", linewidth=1.5, label="Steered to 0 deg")
ax.plot(thetas, steered_mag(thetas, ang_deg), color="#d95f02", linewidth=2, label=f"Steered to {ang_deg:.0f} deg")
ax.axvline(ang_deg, color="#d95f02", linestyle=":")
ax.set_xlabel("Angle from broadside (deg)")
ax.set_ylabel("Normalized |array factor|")
ax.set_title("Steering moves the main lobe to the target's angle")
ax.legend()
plt.tight_layout()
plt.show()

print(f"The beam's main lobe follows the steering angle, here to {ang_deg:.0f} deg.")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
The beam's main lobe follows the steering angle, here to 20 deg.
```

![Notebook output](assets/07/fig_cell22_0.png)

**What this cell does — Steering the beam.**

The phase trick: multiply each element by the conjugate steering vector for the direction you want, and the main lobe moves there. Steered to 0 degrees the lobe sits at broadside; steered to 20 degrees it follows the baseline target.

This scanning-by-phasing is how the radar searches the sky - no mechanical movement, just per-element phase shifts.

## Grating lobes

Earlier we said wide spacing narrows the beam but risks extra main lobes. When the element spacing exceeds half a wavelength, the phase step can reach a full 2 pi *within* the visible range, so the pattern gains a second (and third) main lobe - a **grating lobe**. It looks exactly like the real main lobe, so a radar cannot tell which copy is the true direction.

For d = 3 lambda / 2, the grating lobes land at +-41.8 degrees (where 3 pi sin(theta) = +- 2 pi). Compare that with d = lambda / 2, which has no grating lobes over the visible range. This is why half-wavelength spacing is the standard.

### Notebook cell 24 · code
```python
# Beam pattern for two spacings: half-wavelength vs 1.5 wavelengths.
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))

for i, (spacing_lambda, title) in enumerate([(0.5, "d = lambda/2"), (1.5, "d = 1.5 lambda")]):
    d_test = spacing_lambda * lam
    af = array_factor(np.radians(thetas), n_elements, d_test, lam)
    mn = np.abs(af) / np.abs(af).max()
    ax[i].plot(thetas, mn, color="#7570b3", linewidth=2)
    ax[i].set_title(f"{n_elements} elements, {title}")
    ax[i].set_xlabel("Angle (deg)")
    ax[i].set_ylabel("Normalized |array factor|")
plt.tight_layout()
plt.show()

print("With d = lambda/2 there is one main lobe; with d = 1.5 lambda,")
print("grating lobes appear at +-41.8 deg and are indistinguishable from the true lobe.")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
With d = lambda/2 there is one main lobe; with d = 1.5 lambda,
grating lobes appear at +-41.8 deg and are indistinguishable from the true lobe.
```

![Notebook output](assets/07/fig_cell24_0.png)

**What this cell does — Grating lobes.**

Widen the spacing to 1.5 lambda and the phase can wrap a full 2*pi inside the visible range: the pattern gains whole extra main lobes. Here grating lobes appear at +-41.8 degrees, indistinguishable from the true lobe.

One peak means a trustworthy direction; two equal peaks mean ambiguity. That is why half-wavelength spacing is the standard.

## Checkpoint

In your own words, why does a wave from an off-broadside angle reach the elements of a ULA at different times, and how does that time difference become an angle?

Then answer this: what happens to the beam pattern if you double the element spacing from lambda/2 to lambda, and where do the extra lobes come from?

## Common mistake

A common mistake is to think wider spacing always gives a better (narrower, sharper) beam. It does narrow the main lobe, but it also risks grating lobes that are false copies of the main lobe — so the radar cannot trust where the beam points. Narrower is only better up to the half-wavelength limit; past it you trade an unambiguous direction for a narrower beam.

Another mistake is to forget that the phase step is the *difference* between elements, not the absolute phase at any one element. The absolute phase tells you nothing about direction, because it depends on the total path; only the *relative* phase between neighbouring elements, which depends on the angle, carries direction information.

## Why the helpers exist

The cells above built the geometry, the steering vector, and the array factor step by step so you can see where the phase and the pattern come from. Once the idea is clear, the same work collapses into inter_element_phase_rad, steering_vector, array_factor, and first_null_angle_deg — so the next notebook (and later the full beamforming) can compute a pattern or steer a beam in a single line.

Keep the first pass visible for the physics, then use the helpers when the lesson moves on.

### Notebook cell 28 · code
```python
# The same pattern in helper form, one line per step.
null_h = first_null_angle_deg(n_elements, d_spacing, lam)
steer_h = steering_vector(np.radians(ang_deg), n_elements, d_spacing, lam)
af_h = array_factor(np.radians(thetas), n_elements, d_spacing, lam)

print(f"First null      = {null_h:.1f} deg")
print(f"Steering vector @ {ang_deg:.0f} deg has {steer_h.size} elements")
print(f"|AF| at broadside = {np.abs(af_h).max():.0f} (equals N = {n_elements})")
```

**Executed output:**

```
First null      = 14.5 deg
Steering vector @ 20 deg has 8 elements
|AF| at broadside = 8 (equals N = 8)
```

**What this cell does — The helpers, one line per concept.**

first_null_angle_deg, steering_vector, and array_factor reproduce everything computed by hand: first null 14.5 degrees, an 8-element steering vector, and |AF| peaked at 8 = N at broadside.

The next notebook builds the same tools into an actual angle measurement.

## Stretch: how the number of elements shapes the beam

The beamwidth is set by N (and d). Compare N = 4, 8, and 16 elements at half-wavelength spacing and watch three things: the main lobe narrows, the sidelobes stay at about the same *relative* height but sit closer to the main lobe, and the pattern sharpens overall. A bigger array resolves angles more finely — that is why real radars carry many elements.

### Notebook cell 30 · code
```python
fig, ax = plt.subplots(figsize=(10, 3.5))
for Nn, color in [(4, "#d95f02"), (8, "#1b9e77"), (16, "#7570b3")]:
    af = array_factor(np.radians(thetas), Nn, d_spacing, lam)
    ax.plot(thetas, np.abs(af)/np.abs(af).max(), color=color, linewidth=2, label=f"N={Nn}")
ax.set_xlabel("Angle from broadside (deg)")
ax.set_ylabel("Normalized |array factor|")
ax.set_title("More elements -> narrower main lobe")
ax.legend()
ax.set_xlim(-40, 40)
plt.tight_layout()
plt.show()

for Nn in [4, 8, 16]:
    n0 = first_null_angle_deg(Nn, d_spacing, lam)
    print(f"N={Nn:2d}: first null at {n0:5.1f} deg, beam ~ {2*n0:5.1f} deg wide")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
N= 4: first null at  30.0 deg, beam ~  60.0 deg wide
N= 8: first null at  14.5 deg, beam ~  29.0 deg wide
N=16: first null at   7.2 deg, beam ~  14.4 deg wide
```

![Notebook output](assets/07/fig_cell30_0.png)

**What this cell does — More elements, narrower beam.**

Compare 4, 8, and 16 elements at half-wavelength spacing. The first null moves from 30.0 to 14.5 to 7.2 degrees: beamwidth halves each time N doubles, while sidelobes hold roughly steady in relative height.

Angular resolution comes from aperture size. Four elements give a 60-degree beam, sixteen give 14.4 - real radars carry many elements for exactly this reason.

## Closing the loop: answers to the opening questions

At the start we listed five things to be able to explain. Here is each answer.

**How a line of antennas turns a time difference into an angle.** A wave arriving from angle theta travels an extra path d*sin(theta) to each successive element, so the echo reaches the elements at slightly different times. That delay is a phase shift between elements, and because the extra path depends on sin(theta), the phase difference tells you the angle. The array factor peaks where all elements' phases line up, and the strongest angle is where the target sits.

**What the element spacing is and why half a wavelength.** The elements are spaced d apart along a line. Standard ULA uses d = lambda/2, because then the inter-element phase step pi*sin(theta) stays within +-pi over the whole visible range (+-90 deg), giving exactly one main lobe and no grating lobes. Wider spacing narrows the beam but risks false lobes; narrower spacing is unambiguous but wider.

**How the phase step forms the steering vector.** The inter-element step is Delta_phi = (2 pi d/lambda) sin(theta), and the steering vector stacks one phase per element: a(theta) = [1, e^{j Delta_phi}, e^{j 2 Delta_phi}, ..., e^{j (N-1) Delta_phi}]. It is the pattern of complex echo phases the array records for a wave from theta. For the baseline 20-degree target at half-wavelength spacing, Delta_phi came to 61.6 deg.

**Why the array factor has a main lobe and sidelobes.** Summing the elements coherently gives an array factor whose magnitude rises to N at broadside, where all phases align, and falls where they spread out and cancel. That central hump is the main lobe; the smaller humps where cancellation is incomplete are the sidelobes. With N = 8 elements the first null falls at 14.5 degrees, so the beam is about 29 degrees wide.

**When and why grating lobes appear.** If d exceeds lambda/2, the phase step can reach a full 2 pi inside the visible range, so the pattern gains extra main lobes at directions where it openly "folds" around — grating lobes that look identical to the true main lobe. For d = 1.5 lambda they appeared at +-41.8 degrees. Half-wavelength spacing prevents them.

If you can retell these five answers, you understand how an array measures direction — the final spark that turns a radar from a range-and-velocity sensor into one that can point at a target in the sky.

## Summary

In this notebook you added the third radar measurement — angle — by replacing a single antenna with a uniform linear array. You saw that a wave from an off-broadside angle reaches the elements at different times, and that this path difference d*sin(theta) becomes a phase step between elements.

That phase step builds a steering vector, and summing the elements coherently produces an array factor with a main lobe and sidelobes. You learned why half-wavelength spacing is the standard choice (a single unambiguous main lobe), how steering moves the main lobe to a chosen angle, and how too-wide spacing hides false grating lobes inside the visible range.

An array now points where it listens. The next notebook uses this pattern to actually measure a target's angle (DOA) and shows how a strong interferer can mask a real target.
