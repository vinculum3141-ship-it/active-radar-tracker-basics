# Walkthrough — 09: Beam Steering and Adaptive Nulling

This is a cell-by-cell walkthrough of `beginner/notebooks/09-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 09 — Beam Steering and Adaptive Nulling

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/09-beam-steering-adaptive-nulling.ipynb)

## What this notebook teaches

Notebook 08 scanned the array to *find* a target's direction and showed that a Capon scan can survive a strong interferer. This notebook makes that idea concrete and complete: you will *point* the array at the target with steering weights, and then force a *deep null* on the interferer with linear-constrained minimum-variance (LCMV) weights. Finally you will see the payoff where it counts - the interferer's echo disappears from the range-Doppler map after cancellation, while the target's echo stays.

By the end of this notebook, you should be able to explain:

- what the array weights do and how steering points the main lobe at the target,
- how an LCMV constraint forces a null at the interferer's angle,
- how deep that null is, and why steering alone cannot provide it,
- why the null is applied *before* the matched filter,
- and how an adaptive null removes the interferer from the range-Doppler map while preserving the target.

Keep these five questions in mind as you work through the cells. A dedicated section at the end answers each one directly.

## Setup and baseline values

We reuse the array from Notebooks 07 and 08: 8 elements at half-wavelength spacing, a target at +20 degrees, and a strong interferer at -30 degrees. The scene also carries range and Doppler so we can watch the interference in a range-Doppler map: the target at 1000 m moving at +8 m/s, and the interferer at the same range moving at -8 m/s, 30 dB stronger.

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
from beginner.helpers.array import steering_vector
from beginner.helpers.math import wavelength_m, range_from_delay_samples, delay_samples_for_range
from beginner.helpers.waveforms import lfm_chirp, matched_filter
from beginner.helpers.doppler import build_pulse_stack, range_doppler_map
from beginner.helpers.steering import steering_weights, lcmv_weights
from beginner.helpers.plotting import apply_notebook_style

np.random.seed(42)
apply_notebook_style()
radar_spec = baseline_spec()

lam = wavelength_m(radar_spec.fc_hz)
n_elements = 8
d_spacing = lam / 2.0
angles = np.linspace(-90, 90, 1801)

print(f"8 elements, half-wavelength spacing, lambda = {lam*100:.2f} cm")
print(f"Target at +{radar_spec.target_angle_deg:.0f} deg, interferer at {radar_spec.interferer_angle_deg:.0f} deg")
```

**Executed output:**

```
8 elements, half-wavelength spacing, lambda = 12.24 cm
Target at +20 deg, interferer at -30 deg
```

**What this cell does — Setup: steering and LCMV tools.**

Imports now reach into beginner.helpers.steering for steering_weights and lcmv_weights, plus the full chain: array steering vectors, waveforms, matched filter, pulse stack, and range-Doppler map. The scene: 8 elements, half-wavelength spacing, target +20 degrees, interferer -30 degrees, lambda 12.24 cm.

This notebook also gives the scene range and Doppler - the target at 1000 m moving +8 m/s, the interferer at the same range moving -8 m/s, 30 dB stronger - so we can watch the null act inside a range-Doppler map.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

After Steering and the beam pattern, you know the array can be *pointed*. After DOA, you know it can also be *scanned* and that an adaptive scan survives interference. This notebook pulls it together: instead of just pointing or scanning, you will choose a *weight vector* - the set of complex gains applied to the elements - that both points at the target and cancels the interferer. The rest of this notebook is about how those weights are chosen and what they do to a real range-Doppler map.

## Combining the array is choosing weights

Every way of using the array boils down to one weight vector w: one complex number per element. The combined output is

    y = w^H x

where x is the snapshot at one moment and w^H is the conjugate transpose. The beam pattern you drew in Notebook 07 is just |w^H a(theta)|^2 - how strongly this weighting responds to a wave from each angle theta. So *pointing* the array and *nulling* the interferer are both the same act: picking w.

Before we use the steering and LCMV helper functions, compute the constraint and the target/interferer steering vectors explicitly. This makes the nulling condition obvious: it is not a magical trick, it is a direct requirement that the output be 1 at the target angle and 0 at the jammer angle.

### Notebook cell 9 · code
```python
# Manual target-and-interferer steering vectors for the LCMV constraint.
target_angle = np.radians(20.0)
interferer_angle = np.radians(-30.0)

target_vector = np.exp(1j * np.arange(n_elements) * (2.0 * np.pi * d_spacing * np.sin(target_angle) / lam))
interferer_vector = np.exp(1j * np.arange(n_elements) * (2.0 * np.pi * d_spacing * np.sin(interferer_angle) / lam))

constraint_matrix = np.column_stack([target_vector, interferer_vector])
desired_response = np.array([1.0, 0.0])

print(f"target vector = {np.round(target_vector, 3)}")
print(f"interferer vector = {np.round(interferer_vector, 3)}")
print(f"constraint matrix shape = {constraint_matrix.shape}")
print(f"desired response = {desired_response}")
print(f"This is exactly the requirement C^H w = [1, 0].")
```

**Executed output:**

```
target vector = [ 1.   +0.j     0.476+0.879j -0.547+0.837j -0.997-0.082j -0.403-0.915j
  0.613-0.79j   0.987+0.163j  0.326+0.945j]
interferer vector = [ 1.+0.j  0.-1.j -1.-0.j -0.+1.j  1.+0.j  0.-1.j -1.-0.j -0.+1.j]
constraint matrix shape = (8, 2)
desired response = [1. 0.]
This is exactly the requirement C^H w = [1, 0].
```

**What this cell does — The two steering vectors.**

The constraint math by hand. The target's steering vector at +20 degrees and the interferer's at -30 degrees become the two columns of C; the desired response f = [1, 0] demands unit gain on the target and zero on the interferer.

Note how simple the -30-degree vector is: [1, -j, -1, +j, 1, ...]. The constraint C^H w = [1, 0] is a direct, explicit requirement - no magic.

## Steering the beam at the target

To listen to the target at 20 degrees, choose weights w = a(20)/N - the target's own steering vector, scaled to unit response. These weights line up the elements so a wave from 20 degrees adds coherently (the main lobe points there) and a wave from elsewhere falls apart (the sidelobes are much weaker).

### Notebook cell 11 · code
```python
w_steer = steering_weights(np.radians(20.0), n_elements, d_spacing, lam)

def response_db(w):
    P = np.array([abs(w.conj() @ steering_vector(np.radians(a), n_elements, d_spacing, lam))**2 for a in angles])
    return 10.0 * np.log10(P / P.max())

res_steer = response_db(w_steer)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, res_steer, color="#1b9e77", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="target +20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Response (dB)")
ax.set_title("Steering weights: the main lobe points at +20 deg")
ax.legend()
ax.set_ylim(-40, 2)
plt.tight_layout()
plt.show()

print(f"Main lobe peaks at {angles[np.argmax(res_steer)]:.0f} deg (the target)")
print(f"Response at the interferer (-30 deg): {res_steer[np.argmin(np.abs(angles+30))]:.1f} dB (still leaks through a sidelobe)")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Main lobe peaks at 20 deg (the target)
Response at the interferer (-30 deg): -18.6 dB (still leaks through a sidelobe)
```

![Notebook output](assets/09/fig_cell11_0.png)

**What this cell does — Steer the main lobe at the target.**

steering_weights picks w = a(20)/N, lining up the elements so the +20 direction adds coherently. The main lobe peaks at exactly 20 degrees. But at -30 degrees the response is only -18.6 dB - the beam still leaks through its sidelobe.

That -18.6 dB is the whole problem in one number: pointing at the target does not silence everything else.

## Steering alone cannot reject the interferer

Steering points the beam correctly, but the beam still has sidelobes. At -30 degrees the response is only about -18.6 dB below the main lobe, and our interferer is 30 dB *stronger* than the target. The interferer therefore arrives at the output about 30 - 18.6 = 11 dB above the target even though we steered straight at the target. Steering points, but it does not reject - it has no way to demand a null at the interferer.

## Forcing a null: the LCMV constraint

We want weights that fix two things at once: unit response on the target *and* zero response on the interferer. Write the steering vectors of the target and interferer as the columns of a constraint matrix C = [a(20), a(-30)]. The requirements are

    C^H w = [1, 0]

meaning "respond with gain 1 to the target and gain 0 to the interferer". Among the many weights that satisfy this, the notebook uses the minimum-norm solution, which is the minimum-variance solution for spatially white noise:

    w = C (C^H C)^{-1} f,   f = [1, 0]

This is a constraint-driven way to get the same nulling idea you met with Capon, but now you state the null angle directly instead of scanning for it. A general LCMV design for coloured noise also uses the noise covariance; the expression above is the white-noise case.

### Notebook cell 14 · code
```python
C, f, w_lcmv = lcmv_weights(np.radians(20.0), [-np.radians(30.0)], n_elements, d_spacing, lam)

print("Constraint matrix C, one steering vector per column:")
print(np.round(C, 3))
print(f"\nDesired response f = {f}")
print(f"C^H w = {np.round(C.conj().T @ w_lcmv, 4)}  (should be [1, 0])")

res_lcmv = response_db(w_lcmv)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, res_lcmv, color="#7570b3", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="target +20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Response (dB)")
ax.set_title("LCMV weights: null at -30 deg, target kept at 0 dB")
ax.legend()
ax.set_ylim(-40, 2)
plt.tight_layout()
plt.show()

print(f"Response at the target (+20 deg)  : {res_lcmv[np.argmin(np.abs(angles-20))]:.1f} dB")
print(f"Response at the interferer (-30): {res_lcmv[np.argmin(np.abs(angles+30))]:.1f} dB (deep null)")
```

**Executed output:**

```
Constraint matrix C, one steering vector per column:
[[ 1.   +0.j     1.   +0.j   ]
 [ 0.476+0.879j  0.   -1.j   ]
 [-0.547+0.837j -1.   -0.j   ]
 [-0.997-0.082j -0.   +1.j   ]
 [-0.403-0.915j  1.   +0.j   ]
 [ 0.613-0.79j   0.   -1.j   ]
 [ 0.987+0.163j -1.   -0.j   ]
 [ 0.326+0.945j -0.   +1.j   ]]

Desired response f = [1.+0.j 0.+0.j]
C^H w = [1.+0.j 0.-0.j]  (should be [1, 0])
<Figure size 1000x350 with 1 Axes>
Response at the target (+20 deg)  : -0.0 dB
Response at the interferer (-30): -319.1 dB (deep null)
```

![Notebook output](assets/09/fig_cell14_0.png)

**What this cell does — Forcing a null with the LCMV constraint.**

lcmv_weights solves the constraint C^H w = [1, 0] with the minimum-norm (white-noise) weight vector. The check line shows C^H w = [1, 0] exactly. The pattern now peaks at -0.0 dB on the target and -319.1 dB at the interferer - a deep numerical null.

Sidelobe to deep null: -18.6 dB becomes -319.1 dB. That 300 dB is ideal-array arithmetic; real hardware gets a deep-but-finite null. The target keeps full response either way.

## Before and after: the beam pattern

Overlaying the two response curves makes the change plain. Steering alone leaves a -18.6 dB sidelobe at the interferer; the constrained weights carve a much deeper null. The computed value near -319 dB is limited by floating-point precision, not a promise of real-world rejection. The target keeps full, 0 dB response in both. In this ideal array model, the 30 dB-stronger interferer is rejected at the null angle.

### Notebook cell 16 · code
```python
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, res_steer, color="#1b9e77", linewidth=2, label="steer only (no null)")
ax.plot(angles, res_lcmv, color="#7570b3", linewidth=2, label="LCMV (null at -30)")
ax.axvline(20, color="#d95f02", linestyle=":", label="target +20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="interferer -30 deg")
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Response (dB)")
ax.set_title("Steering vs LCMV: the null changes everything at -30 deg")
ax.legend()
ax.set_ylim(-40, 2)
plt.tight_layout()
plt.show()

i30 = np.argmin(np.abs(angles + 30.0))
print(f"Null depth at -30 deg: {res_lcmv[i30] - res_steer[i30]:.1f} dB improvement over steering alone")
print(f"Target response: {res_steer[np.argmin(np.abs(angles-20))]:.1f} dB (steer) and {res_lcmv[np.argmin(np.abs(angles-20))]:.1f} dB (LCMV)")
```

**Executed output:**

```
<Figure size 1000x350 with 1 Axes>
Null depth at -30 deg: -300.5 dB improvement over steering alone
Target response: 0.0 dB (steer) and -0.0 dB (LCMV)
```

![Notebook output](assets/09/fig_cell16_0.png)

**What this cell does — Before and after, on one plot.**

The two response curves overlaid. Steering alone leaves a -18.6 dB sidelobe at -30 degrees; LCMV carves it down 300.5 dB further. The target stays at 0 dB in both.

This is the answer to 'why is steering not enough': the green curve has no constraint at -30 degrees, the purple one does.

## Checkpoint

In your own words, why does steering toward the target not remove a strong interferer that sits off to the side?

Then explain what the LCMV constraint C^H w = [1, 0] literally demands of the weights, and what that does to the beam at -30 degrees.

## Why this workflow nulls before the matched filter

The weights act on the raw array data, one array snapshot at each fast-time sample, before pulse compression in this implementation. The null uses direction information across the antennas; the matched filter uses echo delay. Combining first reduces the eight channels to one clean signal for subsequent range and Doppler processing. Because these are linear operations, matching all eight channels separately and then beamforming would give the same ideal result. What would fail is discarding the separate channels before their spatial phase pattern has been used.

Let us build the full array scene twice: once with only the target (a clean reference), and once with the interferer 30 dB stronger from -30 degrees. Both use the same noise stream, so the only difference is the interferer.

### Notebook cell 19 · code
```python
pulse_len = int(round(radar_spec.pulse_width_s * radar_spec.fs_hz))
chirp = lfm_chirp(pulse_len, radar_spec.bandwidth_hz, radar_spec.pulse_width_s, radar_spec.fs_hz)
n_delay = delay_samples_for_range(radar_spec.target_range_m, radar_spec.fs_hz)

interferer_amp = 10.0 ** (30.0 / 20.0)  # 30 dB stronger than the target
v_target = 8.0
v_interferer = -8.0
fd_target = 2.0 * v_target / lam
fd_interferer = 2.0 * v_interferer / lam

a20 = steering_vector(np.radians(20.0), n_elements, d_spacing, lam)
am30 = steering_vector(np.radians(-30.0), n_elements, d_spacing, lam)

stack_target = build_pulse_stack(chirp, radar_spec.n_pulses, radar_spec.pri_s, fd_target, n_delay, amplitude=1.0)
stack_interf = build_pulse_stack(chirp, radar_spec.n_pulses, radar_spec.pri_s, fd_interferer, n_delay, amplitude=interferer_amp)

def build_scene(with_interferer):
    rng = np.random.default_rng(42)
    signals = np.zeros((n_elements, radar_spec.n_pulses, stack_target.shape[1]), dtype=complex)
    for n in range(n_elements):
        signals[n] = a20[n] * stack_target + (am30[n] * stack_interf if with_interferer else 0)
        signals[n] += np.sqrt(0.5) * (rng.standard_normal(signals[n].shape) + 1j * rng.standard_normal(signals[n].shape))
    return signals

element_clean = build_scene(False)  # target only: the reference
element_signals = build_scene(True)  # target plus strong interferer

print(f"element_signals shape: {element_signals.shape}  (elements x pulses x fast-time)")
print("Each element carries the target from +20 deg (and, in the second scene, the interferer from -30 deg) plus noise.")
```

**Executed output:**

```
element_signals shape: (8, 64, 533)  (elements x pulses x fast-time)
Each element carries the target from +20 deg (and, in the second scene, the interferer from -30 deg) plus noise.
```

**What this cell does — Build the full 3D array scene.**

The scene becomes three-dimensional: 8 elements x 64 pulses x 533 fast-time samples. Each element carries the target from +20 degrees and (in the second scene) the interferer from -30 degrees at 30 dB, plus complex noise from a fixed seed. The two scenes are identical except for the interferer.

shape (8, 64, 533). The three axes are space (elements), slow time (Doppler), and fast time (range) - the full toolkit working at once.

## Range-Doppler before cancellation

First combine the elements with the *steering-only* weights (point at the target, no null) and then range-compress. The interferer leaks through the -18.6 dB sidelobe, so even though we aimed straight at the target, a loud return from the interferer's direction shows up in the same range bin and muddies the map.

### Notebook cell 21 · code
```python
def beamform_rd(scene, w):
    combined = np.einsum('n,npm->pm', w.conj(), scene)
    profiles = np.array([matched_filter(combined[k], chirp) for k in range(radar_spec.n_pulses)])
    _, vel_axis, rdm = range_doppler_map(profiles, radar_spec.pri_s, radar_spec.fc_hz)
    return rdm, vel_axis

rdm_before, vel_before = beamform_rd(element_signals, w_steer)
range_axis = range_from_delay_samples(np.arange(rdm_before.shape[1]) - (pulse_len - 1), radar_spec.fs_hz)

def bin_value(rdm, vel_axis, vel_mps):
    r = np.argmin(np.abs(range_axis - radar_spec.target_range_m))
    return rdm[np.argmin(np.abs(vel_axis - vel_mps)), r]

# Control reference: target only, steered at the target - no interference at all.
rdm_control, vel_control = beamform_rd(element_clean, w_steer)

fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(rdm_before, aspect="auto", origin="lower",
               extent=[range_axis[0], range_axis[-1], vel_before[0], vel_before[-1]], cmap="viridis")
ax.axvline(radar_spec.target_range_m, color="white", linewidth=0.8, linestyle=":")
ax.set_xlim(700, 1300)
ax.set_ylim(-15, 15)
ax.set_xlabel("Range (m)")
ax.set_ylabel("Velocity (m/s)")
ax.set_title("Range-Doppler before nulling (steer only)")
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.show()

print("Steering-only (no null), target + strong interferer:")
print(f"  target bin (+8 m/s)      = {bin_value(rdm_before, vel_before, v_target):.0f}")
print(f"  interferer bin (-8 m/s)  = {bin_value(rdm_before, vel_before, v_interferer):.0f}  (leaks through the sidelobe)")
print(f"\nReference: target only, no interferer -> target bin = {bin_value(rdm_control, vel_control, v_target):.0f}")
```

**Executed output:**

```
<Figure size 900x500 with 2 Axes>
Steering-only (no null), target + strong interferer:
  target bin (+8 m/s)      = 20743
  interferer bin (-8 m/s)  = 75692  (leaks through the sidelobe)

Reference: target only, no interferer -> target bin = 20200
```

![Notebook output](assets/09/fig_cell21_0.png)

**What this cell does — RDM before nulling: the interferer leaks.**

Beamform with steering-only weights, then matched-filter, then take the range-Doppler map. The -18.6 dB sidelobe is no match for the 30 dB interferer: its Doppler bin reads 75,692 while the target bin reads 20,743. The clean reference (no interferer) gives 20,200 - the interferer has inflated both bins.

The map looks muddy because the loud source at the same range smears across Doppler. A radar trusting it cannot cleanly say where the target is.

## Range-Doppler after cancellation

Now combine the elements with the LCMV weights - the same data, but this time the array itself nulls the interferer *before* the matched filter. The interferer's echo should vanish from its Doppler bin while the target's stays. This is the whole payoff of adaptive nulling: the interference is removed where the array can see it (in angle), so the range-Doppler processing downstream sees only the target.

### Notebook cell 23 · code
```python
rdm_after, vel_after = beamform_rd(element_signals, w_lcmv)

fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(rdm_after, aspect="auto", origin="lower",
               extent=[range_axis[0], range_axis[-1], vel_after[0], vel_after[-1]], cmap="viridis")
ax.axvline(radar_spec.target_range_m, color="white", linewidth=0.8, linestyle=":")
ax.set_xlim(700, 1300)
ax.set_ylim(-15, 15)
ax.set_xlabel("Range (m)")
ax.set_ylabel("Velocity (m/s)")
ax.set_title("Range-Doppler after LCMV nulling")
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.show()

print("After LCMV nulling:")
print(f"  target bin (+8 m/s)      = {bin_value(rdm_after, vel_after, v_target):.0f}")
print(f"  interferer bin (-8 m/s)  = {bin_value(rdm_after, vel_after, v_interferer):.0f}  (nulled to the noise floor)")
```

**Executed output:**

```
<Figure size 900x500 with 2 Axes>
After LCMV nulling:
  target bin (+8 m/s)      = 20198
  interferer bin (-8 m/s)  = 481  (nulled to the noise floor)
```

![Notebook output](assets/09/fig_cell23_0.png)

**What this cell does — RDM after nulling: the interferer disappears.**

The same data, but beamformed with the LCMV weights before the matched filter. The interferer's Doppler bin collapses from 75,692 to 481; the target bin stays at 20,198, essentially the clean-reference 20,200.

That is the whole payoff: the null acts in angle, so the downstream range-Doppler processing sees only the target's echo.

## Before and after: the numbers

Compare the interferer's return before and after, side by side. Before, its Doppler-bin magnitude is about 75,692, versus about 20,743 in the target bin. After the null, the interferer bin drops to about 481, matching the clean-reference noise floor of about 480. The target bin remains near its clean-reference level of about 20,200. These values come from the fixed-seed model scene.

### Notebook cell 25 · code
```python
print(f"target-only reference : target bin = {bin_value(rdm_control, vel_control, v_target):.0f}")
print(f"                       interferer bin = {bin_value(rdm_control, vel_control, v_interferer):.0f}  (noise floor)")
print()
print(f"{'':26}{'steer only':>12}{'LCMV null':>12}")
print(f"{"target bin (+8 m/s)":26}{bin_value(rdm_before, vel_before, v_target):>12.0f}{bin_value(rdm_after, vel_after, v_target):>12.0f}")
print(f"{"interferer bin (-8 m/s)":26}{bin_value(rdm_before, vel_before, v_interferer):>12.0f}{bin_value(rdm_after, vel_after, v_interferer):>12.0f}")
int_before = bin_value(rdm_before, vel_before, v_interferer)
int_after = bin_value(rdm_after, vel_after, v_interferer)
tgt_after = bin_value(rdm_after, vel_after, v_target)
tgt_ref = bin_value(rdm_control, vel_control, v_target)
print()
print(f"Interferer bin: {int_before:.0f} -> {int_after:.0f} (falls to the {bin_value(rdm_control, vel_control, v_interferer):.0f} noise floor)")
print(f"Target bin: {tgt_after:.0f} after nulling vs {tgt_ref:.0f} with no interferer - the target is preserved at its true level.")
```

**Executed output:**

```
target-only reference : target bin = 20200
                       interferer bin = 480  (noise floor)

                            steer only   LCMV null
target bin (+8 m/s)              20743       20198
interferer bin (-8 m/s)          75692         481

Interferer bin: 75692 -> 481 (falls to the 480 noise floor)
Target bin: 20198 after nulling vs 20200 with no interferer - the target is preserved at its true level.
```

**What this cell does — The numbers, side by side.**

The before/after table. Target bin: 20,743 -> 20,198 (reference 20,200). Interferer bin: 75,692 -> 481, which lands on the 480 noise floor. The louder source is removed to the floor; the weaker one is preserved at its true level.

481 vs 480: the null has effectively erased the interferer. These are fixed-seed values, so they reproduce exactly.

## Common mistake

A common mistake is to think steering toward the target should be enough. Steering has no constraint to reject other directions, so it leaves sidelobes that a strong interferer can punch through. Here, 30 dB of input-power advantage minus 18.6 dB of sidelobe attenuation leaves roughly 11.4 dB at the beamformer output. Rejection requires an explicit null, which the constraint adds.

Another mistake is to collapse the eight antenna channels before applying spatial weights. The null uses the phase pattern across those channels. This notebook beamforms the raw array data first, then range-compresses the single output. Because both operations are linear, matching each antenna channel separately and then beamforming would also work if all eight channels remain available; beamforming a previously mixed single channel would not.

## Why the helpers exist

The cells above built the steering weights, solved the LCMV constraint, and applied the weights to the array data by hand so you can see that the whole trick is "choose w". Once the idea is clear, the same work collapses into steering_weights and lcmv_weights - so later notebooks or real experiments can point the array and null a jammer in a couple of lines.

Keep the first pass visible for the weight math, then use the helpers when the lesson moves on.

### Notebook cell 28 · code
```python
# The same weights in helper form.
w_s = steering_weights(np.radians(20.0), n_elements, d_spacing, lam)
C_h, f_h, w_l = lcmv_weights(np.radians(20.0), [-np.radians(30.0)], n_elements, d_spacing, lam)

print(f"steering_weights -> main lobe at {angles[np.argmax(response_db(w_s))]:.0f} deg")
print(f"lcmv_weights     -> constraint matches {np.round(C_h.conj().T @ w_l, 4)}")
```

**Executed output:**

```
steering_weights -> main lobe at 20 deg
lcmv_weights     -> constraint matches [1.+0.j 0.-0.j]
```

**What this cell does — The weights in helper form.**

steering_weights and lcmv_weights reproduce both designs in two lines: main lobe at 20 degrees, constraint matching [1, 0].

Notebook 10 will assemble all of this into the integrated pipeline artifact.

## Stretch: null a second interferer

The LCMV weight vector is not limited to one null - add whatever directions you need. Add a second, weaker interferer at +55 degrees and set up constraints for it too. Re-derive w to null both -30 and +55 degrees while keeping the target at 20. How many nulls can 8 elements support, and where would the design start to break down?

### Notebook cell 30 · code
```python
# Two nulls: -30 deg and +55 deg, target still at +20 deg.
C2, f2, w2 = lcmv_weights(np.radians(20.0), [-np.radians(30.0), np.radians(55.0)], n_elements, d_spacing, lam)
res2 = response_db(w2)

print(f"Constraint check: {np.round(C2.conj().T @ w2, 4)}  (expect [1, 0, 0])")
print(f"Response at target  : {res2[np.argmin(np.abs(angles-20))]:.1f} dB")
print(f"Response at -30 deg : {res2[np.argmin(np.abs(angles+30))]:.1f} dB")
print(f"Response at +55 deg : {res2[np.argmin(np.abs(angles-55))]:.1f} dB")

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(angles, res2, color="#d95f02", linewidth=2)
ax.axvline(20, color="#d95f02", linestyle=":", label="target +20 deg")
ax.axvline(-30, color="#7570b3", linestyle=":", label="null -30 deg")
ax.axvline(55, color="#1b9e77", linestyle=":", label="null +55 deg")
ax.set_ylim(-40, 2)
ax.legend()
ax.set_xlabel("Angle (deg)")
ax.set_ylabel("Response (dB)")
ax.set_title("LCMV with two nulls")
plt.tight_layout()
plt.show()
```

**Executed output:**

```
Constraint check: [ 1.+0.j  0.-0.j -0.-0.j]  (expect [1, 0, 0])
Response at target  : -0.0 dB
Response at -30 deg : -310.3 dB
Response at +55 deg : -307.5 dB
<Figure size 1000x350 with 1 Axes>
```

![Notebook output](assets/09/fig_cell30_0.png)

**What this cell does — Stretch: null two interferers.**

LCMV scales to any number of constraints. Add a second interferer at +55 degrees and the solver produces C^H w = [1, 0, 0]: both sources nulled (about -310 and -308 dB) while the target keeps 0 dB.

The real limit is degrees of freedom: 8 elements can satisfy at most 8 constraints before the weight design breaks down. Each null costs an element's worth of freedom.

## Closing the loop: answers to the opening questions

At the start we listed five things to be able to explain. Here is each answer.

**What the array weights do and how steering points the lobe.** Every way of using the array reduces to one weight vector w, one complex gain per element. Steering chooses w = a(target)/N so a wave from the target's direction adds coherently and everything else falls into sidelobes; the main lobe points exactly at the target.

**How an LCMV constraint forces a null.** You collect the steering vectors of the target and interferer into C and demand C^H w = [1, 0] - unit response on the target, zero on the interferer. Solving w = C (C^H C)^{-1} f picks the weights that satisfy it while minimising output power.

**How deep the null is and why steering alone cannot give it.** The LCMV null at -30 degrees sat at about -319 dB, limited by numerical precision, versus the -18.6 dB sidelobe that steering alone left. Steering only points the main lobe; it has no constraint to reject other directions, so a loud source can punch through a sidelobe.

**Why the null happens before the matched filter.** The null is a spatial operation on the array snapshot - which angle a wave came from - while the matched filter is a temporal one - how far away it is. Cancelling in space first leaves a clean temporal signal to range- and Doppler-process.

**How the null removes the interferer from the range-Doppler map.** With steering-only weights the strong interferer fell at its -30 degree direction and inflated both Doppler bins at the target's range, so the map was muddled. After the LCMV null the interferer's own bin collapsed back to the noise floor while the target's bin matched the clean, interferer-free reference - the interferer is gone and the target is preserved.

If you can retell these five answers, you can point an array and deliberately silence a jammer while keeping the target - the sharpest tool in the beamforming kit.

## Summary

In this notebook you turned beamforming into a design choice. You steered the main lobe at the target with steering weights, then forced a deep null on the interferer with LCMV constraints C^H w = [1, 0]. The beam pattern showed the payoff: steering left a -18.6 dB sidelobe at the interferer, LCMV carved it down to about -319 dB while keeping the target at 0 dB.

You then applied the weights *before* the matched filter - the correct order, because the null is spatial and pulse compression is temporal. On the range-Doppler map, the 30 dB-stronger interferer's echo disappeared from its Doppler bin (falling back to the noise floor) while the target's echo matched its clean, interferer-free level. With range, velocity, direction, and now the ability to cancel interference by choice, you have the complete toolkit. The final notebook ties the whole chain together and assembles the portfolio artifacts.
