# Walkthrough — 06: Kalman Tracking

This is a cell-by-cell walkthrough of `beginner/notebooks/06-*.ipynb`. Every notebook cell is reproduced verbatim; the annotation paragraphs explain the code, the physics, and the result. Each figure output is inlined where it appears in the notebook.

---

# 06 — Kalman Tracking

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vinculum3141-ship-it/active-radar-tracker-basics/blob/radar-tracker-notebooks/beginner/notebooks/06-kalman-tracking.ipynb)

## What this notebook teaches

Notebook 05 ended with a range-Doppler map: one bright blob giving a target's range *and* velocity in a single glance. That is one measurement. On its own it is noisy, and a moving target gives you a new one every CPI. This notebook shows how many noisy measurements are turned into one smooth, stable estimate of where the target is and where it is going, using a Kalman filter.

By the end of this notebook, you should be able to explain:

- why a single noisy detection is not enough to know where a target is,
- what the *predict* step does and why its guess is uncertain,
- what the *update* step does with each new measurement,
- how the filter decides how much to trust the model versus the sensor,
- and why the filtered track is smoother than the raw measurements.

Keep these five questions in mind as you work through the cells. A dedicated section at the end answers each one directly.

## Setup and baseline values

The shared helpers give you the baseline radar parameters and the Doppler tools from Notebook 05. This notebook adds one new idea: a *filter* that fuses the noisy range and velocity detections into a smooth track over time.

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
radar_spec
```

**Executed output:**

```
BaselineRadarSpec(fc_hz=2450000000.0, bandwidth_hz=5000000.0, pulse_width_s=2e-05, pri_s=0.001, fs_hz=20000000.0, n_pulses=64, target_range_m=1000.0, target_velocity_mps=40.0, snr_db=20.0, target_angle_deg=20.0, interferer_angle_deg=-30.0)
```

**What this cell does — Setup: constants for the tracker.**

Imports the baseline spec, the wavelength helper, and the notebook style. The seed is fixed at 42 so the noisy detections - and every number in this lesson - are reproducible.

No signal processing is needed here; the input is a stream of (range, velocity) measurements from the range-Doppler map of Notebook 05.

## Teach it directly first
Before we call the reusable helper, we do the core calculation here by hand so the physics stays visible. The helper is the same idea packaged for reuse later in the course; it is not a replacement for understanding the math.
This notebook keeps the direct implementation visible at the first encounter, then reuses the helper as the clean, repeated version.

## Where we are in the story

Notebook 05 produced a range-Doppler map for one batch of pulses. We re-read that map every *coherent processing interval* (CPI) - one CPI is N pulses of PRI each, here 64 x 1 ms = 64 ms - so a target gives you a fresh (range, velocity) detection every 64 ms.

That flow of detections is the input to this notebook. Each detection is roughly right but never exact: the peak wobbles around the true value. This notebook builds a filter that watches the sequence and produces a track far steadier than any single reading.

## The problem: one noisy measurement is not enough

Let us watch a target that starts at 1000 m and moves toward you at a steady 20 m/s (inside the unambiguous band, so the measurement is honest). Over 50 CPIs - about 3.2 seconds - we get 50 detections, each with a range and a velocity.

Each detection is the true value plus noise, as if the map's peak were nudged around by the thermal noise you met in Notebook 03. Plotted alone, the detections dance around the truth. A single one could be off by many metres. If you steered by one reading you would chase noise.

### Notebook cell 9 · code
```python
# True trajectory: start at 1000 m, move toward you at 20 m/s.
# One measurement arrives per CPI = n_pulses * PRI = 64 * 1 ms = 64 ms.
dt_s = radar_spec.n_pulses * radar_spec.pri_s          # 0.064 s per CPI
n_steps = 50
r_true = 1000.0 + 20.0 * np.arange(n_steps) * dt_s     # metres
v_true = np.full(n_steps, 20.0)                        # m/s

# The map reads the true value, then we add measurement noise.
sigma_r = 5.0     # m   - typical spread of the range peak
sigma_v = 1.5     # m/s - typical spread of the velocity peak
z_range = r_true + sigma_r * np.random.randn(n_steps)
z_vel   = v_true + sigma_v * np.random.randn(n_steps)

print(f"CPI duration = {dt_s*1000:.0f} ms; {n_steps} CPIs = {n_steps*dt_s:.1f} s of observation")
print(f"Measurement noise: +-{sigma_r:.0f} m in range, +-{sigma_v:.1f} m/s in velocity")
```

**Executed output:**

```
CPI duration = 64 ms; 50 CPIs = 3.2 s of observation
Measurement noise: +-5 m in range, +-1.5 m/s in velocity
```

**What this cell does — Generate the detections.**

The scenario: a target at 1000 m approaching at 20 m/s, observed for 50 CPIs, each CPI = 64 x 1 ms = 64 ms, for 3.2 s total. Each detection is the true value plus Gaussian noise: +-5 m in range, +-1.5 m/s in velocity.

Everything downstream uses these 50 noisy points. There is no complaint about the noise: it is the honest output of the range-Doppler map.

## True versus measured

The plot shows both the true trajectory (a clean, straight line in range) and what the detector saw (the noisy points). The straight line is the ground truth the radar never knows; the scatter is what it actually measures. Your job as the filter is to recover the straight line from the scatter.

### Notebook cell 11 · code
```python
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))

t_s = np.arange(n_steps) * dt_s
ax[0].plot(t_s, r_true, color="#1b9e77", linewidth=2, label="True range")
ax[0].plot(t_s, z_range, ".", color="#d95f02", alpha=0.7, label="Measured range")
ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Range (m)")
ax[0].set_title("Range: true vs measured")
ax[0].legend()

ax[1].plot(t_s, v_true, color="#1b9e77", linewidth=2, label="True velocity")
ax[1].plot(t_s, z_vel, ".", color="#d95f02", alpha=0.7, label="Measured velocity")
ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Velocity (m/s)")
ax[1].set_title("Velocity: true vs measured")
ax[1].legend()
plt.tight_layout()
plt.show()

print(f"A single measured range can be off by up to about {3*sigma_r:.0f} m (3 sigma).")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
A single measured range can be off by up to about 15 m (3 sigma).
```

![Notebook output](assets/06/fig_cell11_0.png)

**What this cell does — True versus measured.**

Two panels. Green: the clean straight-line truth the radar never sees. Orange dots: what the detector actually reports. A single measured range can be off by up to about 15 m at 3 sigma - enough that steering by one reading would chase noise.

The filter's job is to recover the green line from the orange points.

## The insight: blend a guess with a measurement

You could smooth the scatter by averaging, but a moving target cannot be a simple average - at 20 m/s it travels about 1.3 m per CPI, so the range genuinely changes every step. The filter needs to do something smarter.

The Kalman filter keeps an *estimate* that combines two sources of information:

- **A prediction from the model.** If you knew the range and velocity a moment ago, you can guess where the target is now, because it moves smoothly. This guess is informed but imperfect - the model may not be perfectly true.
- **A fresh measurement.** Each CPI gives you a direct, noisy reading of range and velocity. This is honest but jittery.

Neither is trusted alone. The filter weighs them by how trustworthy each is and produces a blended estimate that is better than either input. That weighing is the whole filter.

## The state: what the filter thinks it knows

The filter's belief is packaged in two objects.

- **The state vector** x = [range, velocity]. This is the filter's best guess of the target's position and speed right now.
- **The covariance matrix** P. This encodes how *unsure* the filter is about that guess - how far the true state might lie from x. Big diagonal entries mean big uncertainty.

Both are updated every step. Uncertainty grows when the model is applied (we are not sure the target obeys it perfectly) and shrinks when a good measurement arrives (the sensor pins us down).

We also need two numbers that we set ahead of time: **Q**, the process noise, describing how much the model is trusted (how strongly the target really obeys constant velocity), and **R**, the measurement noise, describing how much the sensor is trusted (how noisy the detections are).

## Step 1: predict from the model

The first half of each timestep uses *only* the model, no new measurement. If the current estimate is range r and velocity v, then after a time dt the best guess of the new state is:

- new range = r + v*dt  (the target keeps moving)
- new velocity = v       (constant-velocity model)

That is a matrix multiplication by the transition matrix F = [[1, dt], [0, 1]]. The covariance grows by adding Q, because we are not fully sure the target holds its velocity.

Let us run one prediction by hand on the first step and look at the numbers.

Before the helper-based filter code, compute the 2x2 state update explicitly for the first time step. This is the same algebra the filter uses, just written out in a way that a beginner can follow.

### Notebook cell 15 · code
```python
# Manual constant-velocity prediction for the first step.
dt = dt_s
F = np.array([[1.0, dt], [0.0, 1.0]])
x_guess = np.array([z_range[0], 0.0])
P_guess = np.diag([20.0, 20.0])
Q = np.array([[0.5, 0.0], [0.0, 0.5]])

x_pred = F @ x_guess
P_pred = F @ P_guess @ F.T + Q

print(f"x_guess = {x_guess}")
print(f"F x_guess = {x_pred}")
print(f"P_pred =\n{P_pred}")
print(f"This is the model's best guess before the measurement arrives.")
```

**Executed output:**

```
x_guess = [1002.48357077    0.        ]
F x_guess = [1002.48357077    0.        ]
P_pred =
[[20.58192  1.28   ]
 [ 1.28    20.5    ]]
This is the model's best guess before the measurement arrives.
```

**What this cell does — One prediction, by hand.**

The first half of the loop uses only the model. Constant velocity: new range = r + v*dt, velocity unchanged, written as F = [[1, dt],[0, 1]]. The first-measurement guess, 1002.48 m at 0 m/s, predicts to itself because the velocity is unknown; the covariance grows through F@P@F.T + Q.

The covariance growth is the honest statement: running the model forward adds uncertainty, because the target may not perfectly obey constant velocity.

### Notebook cell 16 · code
```python
# One prediction step, written out.
dt = dt_s                                  # 0.064 s
F = np.array([[1.0, dt], [0.0, 1.0]])      # constant-velocity transition

# Guess the initial state from the first measurement; velocity unknown.
x = np.array([z_range[0], 0.0])
P = np.diag([20.0, 20.0])                  # start fairly unsure
Q = np.array([[0.5, 0.0], [0.0, 0.5]])     # small process noise

x_pred = F @ x
P_pred = F @ P @ F.T + Q

print(f"State before predict  : range {x[0]:.2f} m, vel {x[1]:.2f} m/s")
print(f"After predict         : range {x_pred[0]:.2f} m, vel {x_pred[1]:.2f} m/s")
print(f"Uncertainty (P range) : {P_pred[0,0]:.2f} -> grew because the model is not perfect")
```

**Executed output:**

```
State before predict  : range 1002.48 m, vel 0.00 m/s
After predict         : range 1002.48 m, vel 0.00 m/s
Uncertainty (P range) : 20.58 -> grew because the model is not perfect
```

**What this cell does — The same prediction, in numbers.**

The prediction with real numbers: state 1002.48 m / 0.00 m/s stays 1002.48 m / 0.00 m/s, because the filter started with zero velocity, and the range uncertainty grows from 20.00 to 20.58.

This cell exists so you see the matrix product and the printed numbers agreeing.

## Step 2: update with the measurement

The second half fuses the prediction with the new detection. We look at the difference between what the model predicted and what the sensor measured - the *innovation* z - x_pred. Then we decide how much of that difference to accept.

That decision is the **Kalman gain** K. It is computed from the two uncertainties:

- If the measurement is very trustworthy relative to the prediction (R small, P large), K is close to 1 and we mostly follow the measurement.
- If the prediction is very trustworthy relative to the measurement (P small, R large), K is close to 0 and we mostly keep the prediction.

The filter always lands somewhere in between, and the gain is recomputed every step as the uncertainties change. The update is:

- new_state = prediction + K * (measurement - prediction)
- new_covariance = prediction_covariance adjusted down by the gain.

Let us finish the first step by hand.

### Notebook cell 18 · code
```python
# One update step, written out, fusing the prediction with the new detection.
H = np.eye(2)                                # we measure both range and velocity
R = np.diag([sigma_r**2, sigma_v**2])        # measurement noise covariance

z = np.array([z_range[0], z_vel[0]])          # first detection

S = H @ P_pred @ H.T + R
K = P_pred @ H.T @ np.linalg.inv(S)           # Kalman gain (2x2 here)
innovation = z - H @ x_pred
x_new = x_pred + K @ innovation
P_new = (np.eye(2) - K @ H) @ P_pred

print(f"Prediction        : range {x_pred[0]:.2f} m, vel {x_pred[1]:.2f} m/s")
print(f"Measurement       : range {z[0]:.2f} m, vel {z[1]:.2f} m/s")
print(f"Kalman gain       : K_range={K[0,0]:.2f}, K_vel={K[1,1]:.2f}")
print(f"Updated estimate  : range {x_new[0]:.2f} m, vel {x_new[1]:.2f} m/s")
```

**Executed output:**

```
Prediction        : range 1002.48 m, vel 0.00 m/s
Measurement       : range 1002.48 m, vel 20.49 m/s
Kalman gain       : K_range=0.45, K_vel=0.90
Updated estimate  : range 1003.12 m, vel 18.46 m/s
```

**What this cell does — One update, by hand.**

The second half fuses prediction and measurement. The innovation - measurement minus prediction - is about 0 m and +20.49 m/s: the sensor has finally supplied the velocity. The Kalman gain splits the difference, K_range = 0.45, K_vel = 0.90, and the estimate moves to 1003.12 m and 18.46 m/s.

Because the prediction carried zero velocity while the sensor says 20.49, the filter trusts the sensor more on velocity (K = 0.90) than on range (K = 0.45). A gain near 1 means 'believe the measurement'.

## Run the loop over every CPI

One step is a prediction then an update. Repeating that over all 50 CPIs produces the whole track. The filter never needs to remember the full history - it keeps just the state and the covariance, and carries them forward. That is what makes it a *recursive* filter: each new measurement is folded in with only the latest belief, not all past data.

Let us run the loop and collect the filtered estimates.

### Notebook cell 20 · code
```python
# Run predict + update for every measurement; collect each posterior.
x = np.array([z_range[0], 0.0])
P = np.diag([20.0, 20.0])
Q = np.array([[0.5, 0.0], [0.0, 0.5]])
H = np.eye(2)
R = np.diag([sigma_r**2, sigma_v**2])

filtered_range = np.zeros(n_steps)
filtered_vel = np.zeros(n_steps)
gain_trace = np.zeros(n_steps)

for k in range(n_steps):
    # predict
    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    # update
    z = np.array([z_range[k], z_vel[k]])
    S = H @ P_pred @ H.T + R
    K = P_pred @ H.T @ np.linalg.inv(S)
    x = x_pred + K @ (z - H @ x_pred)
    P = (np.eye(2) - K @ H) @ P_pred
    filtered_range[k] = x[0]
    filtered_vel[k] = x[1]
    gain_trace[k] = K[0, 0]

print(f"Final filtered: range {filtered_range[-1]:.1f} m, velocity {filtered_vel[-1]:.2f} m/s")
print(f"True final     : range {r_true[-1]:.1f} m, velocity {v_true[-1]:.2f} m/s")
```

**Executed output:**

```
Final filtered: range 1060.8 m, velocity 19.80 m/s
True final     : range 1062.7 m, velocity 20.00 m/s
```

**What this cell does — Run the full loop.**

Repeat predict then update 50 times and the recursion does its work. The final filtered estimate is 1060.8 m and 19.80 m/s against the true 1062.7 m and 20.00 m/s. Only the latest state and covariance were ever carried forward - that is what makes the filter recursive.

Look at how close the finals are. From 50 noisy measurements the filter pins range to within 2 m and velocity to within 0.2 m/s.

## The track: smoother than any measurement

Here are all three lines together: the true trajectory the radar never sees, the noisy measurements it does see, and the filtered track it estimates. The filtered line is much steadier than the scatter, and it hugs the true line. That is the point of the notebook - noisy detections in, a stable track out.

### Notebook cell 22 · code
```python
fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))

ax[0].plot(t_s, r_true, color="#1b9e77", linewidth=2, label="True")
ax[0].plot(t_s, z_range, ".", color="#d95f02", alpha=0.4, label="Measured")
ax[0].plot(t_s, filtered_range, color="#7570b3", linewidth=2, label="Filtered")
ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Range (m)")
ax[0].set_title("Range track")
ax[0].legend()

ax[1].plot(t_s, v_true, color="#1b9e77", linewidth=2, label="True")
ax[1].plot(t_s, z_vel, ".", color="#d95f02", alpha=0.4, label="Measured")
ax[1].plot(t_s, filtered_vel, color="#7570b3", linewidth=2, label="Filtered")
ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Velocity (m/s)")
ax[1].set_title("Velocity track")
ax[1].legend()
plt.tight_layout()
plt.show()

err_zr = np.sqrt(np.mean((z_range - r_true)**2))
err_fr = np.sqrt(np.mean((filtered_range - r_true)**2))
err_zv = np.sqrt(np.mean((z_vel - v_true)**2))
err_fv = np.sqrt(np.mean((filtered_vel - v_true)**2))
print(f"Range   RMS error: measured {err_zr:.2f} m  vs  filtered {err_fr:.2f} m")
print(f"Velocity RMS error: measured {err_zv:.2f} m/s  vs  filtered {err_fv:.2f} m/s")
```

**Executed output:**

```
<Figure size 1200x350 with 2 Axes>
Range   RMS error: measured 4.76 m  vs  filtered 1.84 m
Velocity RMS error: measured 1.30 m/s  vs  filtered 0.59 m/s
```

![Notebook output](assets/06/fig_cell22_0.png)

**What this cell does — The track: smoother than any measurement.**

The payoff. Range RMS error drops from 4.76 m (raw) to 1.84 m (filtered); velocity from 1.30 m/s to 0.59 m/s. The filtered lines hug the green truth while the raw measurements scatter around it.

This is not smoothing by averaging - the predict step keeps the track from lagging a moving target. Improvement is about 2.6x in range, 2.2x in velocity.

## How trust shifts: the Kalman gain over time

The gain is not a fixed constant - it adapts. Early on, the filter is very unsure (P is large because it started cold), so it leans heavily on each measurement and the gain is high. As more measurements arrive and P shrinks, the filter trusts its own estimate more and the gain settles to a lower, steady value.

Plotting the gain across the track shows this: a fast start, then convergence to a stable blend. That balance - how much to trust the model versus the sensor - is the central idea of the filter.

### Notebook cell 24 · code
```python
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(t_s, gain_trace, color="#7570b3", linewidth=2)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Kalman gain (range)")
ax.set_title("The filter trusts measurements less as its own estimate firms up")
plt.tight_layout()
plt.show()

print(f"Gain starts near {gain_trace[0]:.2f} and settles to about {gain_trace[-1]:.2f}.")
```

**Executed output:**

```
<Figure size 1000x300 with 1 Axes>
Gain starts near 0.45 and settles to about 0.13.
```

![Notebook output](assets/06/fig_cell24_0.png)

**What this cell does — The gain learns to trust the model.**

Plotting the Kalman gain shows the adaptation. It starts near 0.45 and settles to about 0.13: early, the filter was cold with large uncertainty and leaned on measurements; as the covariance shrank, it trusted its own model more.

That downward curve is the filter learning the scene. The gain is never hand-tuned - it is recomputed from P, Q, and R at every step.

## Checkpoint

In your own words, what does the *predict* step do, and what does the *update* step do with a new measurement?

Then answer this: if the measurement noise were much larger (bigger R), would the filter trust the measurements more or less? What would happen to its estimate?

## Common mistake

A common mistake is to think the filter simply averages the measurements. It does not - if the target is *moving*, a plain average of past positions lags behind the truth. The Kalman filter predicts where the target should be now (using velocity), then blends in the latest measurement. The predict step is what lets the track keep up with a moving target instead of trailing it.

Another mistake is to treat the gain as a fixed constant to be tuned by hand. The gain is *derived* from the uncertainties P, Q, and R at each step; you tune the covariances (how much you trust the model and the sensor), and the gain follows. Set R too small and the filter chases every bit of measurement noise; set R too large and it ignores the sensor and drifts.

## Why the helpers exist

The cells above ran predict and update step by step so you can see where the estimate and the uncertainty come from. Once the idea is clear, the same work collapses into state_transition_matrix, predict, update, and run_kalman_track - so the later notebooks (and the automated radar) can fuse detections in a few lines instead of a full loop.

Keep the first pass visible for the filter's logic, then use the helpers when the lesson moves on.

### Notebook cell 28 · code
```python
# The same track in helper form.
from beginner.helpers.kalman import state_transition_matrix, run_kalman_track

measurements = np.stack([z_range, z_vel], axis=1)
Fh = state_transition_matrix(dt_s)
Qh = np.array([[0.5, 0.0], [0.0, 0.5]])
Hh = np.eye(2)
Rh = np.diag([sigma_r**2, sigma_v**2])
x0 = np.array([z_range[0], 0.0])
P0 = np.diag([20.0, 20.0])

pred_h, filt_h, cov_h, gain_h = run_kalman_track(measurements, Fh, Qh, Hh, Rh, x0, P0)

err_h = np.sqrt(np.mean((filt_h[:, 0] - r_true)**2))
print(f"Helper filtered range RMS error = {err_h:.2f} m (matches the hand-built loop)")
```

**Executed output:**

```
Helper filtered range RMS error = 1.84 m (matches the hand-built loop)
```

**What this cell does — The same track from the helpers.**

run_kalman_track reproduces the whole loop in one call, and the RMS error comes out identical: 1.84 m.

Later notebooks (and the automated radar) use exactly this helper instead of the loop in the by-hand cell.

## Stretch: two targets

A real scene has more than one target. Run the same track twice - once for a target at 1000 m moving at 20 m/s, once for a second target at 1500 m moving away at 10 m/s - and plot both filtered tracks against their (noisy) measurements. The filter keeps each track separate; it never blends the two targets' detections, because each has its own state.

### Notebook cell 30 · code
```python
# Track two independent targets through the same filter.

def simulate_target(r0, v):
    trace_r = r0 + v * np.arange(n_steps) * dt_s
    trace_v = np.full(n_steps, v)
    zr = trace_r + sigma_r * np.random.randn(n_steps)
    zv = trace_v + sigma_v * np.random.randn(n_steps)
    m = np.stack([zr, zv], axis=1)
    _, filt, _, _ = run_kalman_track(m, Fh, Qh, Hh, Rh, np.array([zr[0], 0.0]), P0)
    return trace_r, trace_v, zr, filt

tr1_r, tr1_v, z1_r, f1 = simulate_target(1000.0, 20.0)
tr2_r, tr2_v, z2_r, f2 = simulate_target(1500.0, -10.0)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t_s, tr1_r, color="#1b9e77", linewidth=2, label="Target 1 true")
ax.plot(t_s, z1_r, ".", color="#1b9e77", alpha=0.3)
ax.plot(t_s, f1[:, 0], color="#1b9e77", linewidth=2, linestyle="--", label="Target 1 filtered")
ax.plot(t_s, tr2_r, color="#d95f02", linewidth=2, label="Target 2 true")
ax.plot(t_s, z2_r, ".", color="#d95f02", alpha=0.3)
ax.plot(t_s, f2[:, 0], color="#d95f02", linewidth=2, linestyle="--", label="Target 2 filtered")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Range (m)")
ax.set_title("Two targets tracked independently")
ax.legend()
plt.tight_layout()
plt.show()

print(f"Target 1 filtered velocity settles to {f1[-1,1]:.1f} m/s (true 20)")
print(f"Target 2 filtered velocity settles to {f2[-1,1]:.1f} m/s (true -10)")
```

**Executed output:**

```
<Figure size 1000x400 with 1 Axes>
Target 1 filtered velocity settles to 19.3 m/s (true 20)
Target 2 filtered velocity settles to -9.2 m/s (true -10)
```

![Notebook output](assets/06/fig_cell30_0.png)

**What this cell does — Two targets, two tracks.**

The stretch: two independent targets - 1000 m approaching at 20 m/s and 1500 m receding at -10 m/s. The filter keeps the tracks separate, each settling to its own velocity: 19.3 m/s and -9.2 m/s.

Each target has its own state and covariance, and they never leak into each other. Multi-target tracking is running the same filter twice.

## Closing the loop: answers to the opening questions

At the start we listed five things to be able to explain. Here is each answer.

**Why a single noisy detection is not enough.** Each detection is the true range and velocity plus noise. Read alone, a single measurement can be off by several metres or m/s, so steering by one reading would chase noise. The track needs to combine many readings and use the knowledge that the target moves smoothly.

**What the predict step does.** Predict uses only the model: it advances the state by dt with the constant-velocity transition (range grows by v*dt, velocity unchanged) and grows the covariance by the process noise Q, because the model is not perfect. It answers "where do I expect the target to be now?" before looking at the new measurement.

**What the update step does.** Update fuses the prediction with a new measurement. It forms the innovation (measurement minus prediction), weights it by the Kalman gain K, and adds that weighted correction to the prediction. Then it shrinks the covariance, because the measurement has reduced the uncertainty.

**How the filter balances model and sensor.** The Kalman gain K is derived from the two uncertainties. When the sensor is trustworthy relative to the prediction (R small, P large), K is near 1 and the filter follows the measurement. When the prediction is trustworthy (P small, R large), K is near 0 and the filter keeps its prediction. The balance is recomputed every step. Larger R means less trust in the sensor: K shrinks, the estimate leans more on the model, and the filter does not chase the noisier measurements (at the cost of ignoring valid new information).

**Why the filtered track is smoother.** The filter averages information across many detections while still tracking motion. Measurement noise tends to cancel out when combined, so the filtered range and velocity wobble far less than any single measurement, while the predict step keeps the track from lagging a moving target. The RMS error versus truth dropped - in our run the filtered range error was well below the single-measurement error.

If you can retell these five answers, you have turned a stream of noisy detections into a stable estimate of where a target is and where it is going.

## Summary

In this notebook you built a Kalman filter that turns the noisy range and velocity detections from a range-Doppler map into a smooth, stable track. You saw that a single measurement is not trustworthy on its own, and that the filter keeps two things - a state vector (range and velocity) and a covariance (uncertainty).

Each timestep is two halves. The predict step advances the state with a constant-velocity model and grows the uncertainty. The update step fuses in the newest detection, weighted by the Kalman gain that balances trust in the model against trust in the sensor. Because the gain is recomputed from the current uncertainties, the filter starts by leaning on measurements and settles into a steady, well-balanced estimate.

The result is a track far smoother than any raw measurement, and (from the stretch) a filter that can run several independent tracks at once. Range and velocity are no longer single snapshots - they are a continuously updated picture of the scene. That picture is what the remaining notebooks will refine with angle and interference.
