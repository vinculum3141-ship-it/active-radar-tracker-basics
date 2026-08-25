# 09 — Notebook Playbook

This document is the trainer-facing build plan for the learner notebooks.
It converts the training spine into a concrete production sequence so the
notebooks can be written quickly, consistently, and in the right order.

The rule is simple: build the notebooks around the physics and learning goals
first, and only use code as the demonstration vehicle. Shared notebook
functionality lives directly under `beginner/` in a small helper structure.

Shared notebook functionality lives directly under `beginner/helpers/` in a small helper structure.
---

## 1. Purpose

The playbook exists to minimize rework.

It answers four questions before any notebook is written:

1. What is the learning goal of this notebook?
2. What concepts must already be known?
3. What must the learner see, compute, and explain?
4. What should the trainer say, show, and check?

If a notebook cannot answer those four questions, it is not ready to build.

---

## 2. Build order

Build in this sequence to move fastest:

1. Lock the notebook spine and titles.
2. Define the beginner-local helper structure and import rules.
3. Write the shared notebook template and teaching style.
4. Draft trainer notes for every notebook before writing code cells.
5. Build Notebook 0 and Notebook 1 first to establish the pattern.
6. Build the remaining notebooks in dependency order.
7. Add review exercises and checkpoint questions after each notebook.
8. Add the extension notebooks only after the core spine is complete.

This sequence avoids the common mistake of writing code before the lesson arc.

---

## 3. Shared notebook template

Every notebook should follow the same internal structure so learners do not
have to relearn the format each time.

### Required sections inside each notebook

1. Title and purpose.
2. What the learner already knows.
3. The one new concept of the notebook.
4. The one governing equation or relationship.
5. Guided code cells that reveal the idea in small steps.
6. One visual interpretation cell.
7. One checkpoint question.
8. One short exercise or lab prompt.
9. A recap cell with the “what to remember” summary.

### Required notebook style

- Address the reader directly as **you**; never use "the learner" in a learner-facing notebook.
- Use short markdown explanations before code.
- Keep code cells small and incremental.
- Show intermediate values, not only final plots.
- Seed all randomness.
- Prefer a single concept per code cell.
- End with a learner prompt or observation question.

### What not to do

- Do not dump the full implementation at the start.
- Do not mix too many new concepts in one notebook.
- Do not bury the physics under utilities or helper classes.
- Do not make the notebook depend on hidden state from prior notebooks.

---

## 3b. Learner handbook style

The learner handbook (`beginner/learner_guide.md`) is a companion to the notebooks.
It is the deeper, slower read — the place where a learner goes when a notebook
cell does not click, or when they want the full story before running the code.

### Audience

- The reader is the learner, not the trainer.
- The trainer guide tells you *how to teach*; the learner handbook tells you
  *what the concept means*.

### Required structure per chapter

1. Open with the same learning objectives as the notebook.
2. Walk through the concepts in narrative form, with equations and diagrams.
3. Reference specific notebook cells by name or section heading — do not
   duplicate the code or output.
4. Close with expanded "closing the loop" answers that add physical intuition
   beyond what the notebook provides.

### Scope boundaries

- Each chapter is **2–3× the prose** of the notebook markdown, not a textbook
  chapter.
- Reference the notebook cell; do not repeat the code, output, or plots.
- One concept per section, same as the notebook.
- No executable code blocks — this is reading, not running.
- Do not introduce new equations or helper functions that the notebook does not
  use. If the notebook calls `matched_filter`, the handbook explains what
  correlation means; it does not redefine the helper.
- Do not duplicate the trainer guide. If a point is about *how to teach* rather
  than *what the concept means*, it belongs in the trainer guide, not the
  handbook.

### Cross-referencing convention

- When the handbook discusses a computation, point to the specific notebook cell:
  "See the calculation cell in Notebook 03" or "In the correlation-by-hand cell..."
- When the trainer guide discusses a concept, point to the handbook:
  "The full derivation is in the learner handbook, Chapter 03, §Correlation by hand."
- This keeps the three layers connected without duplicating content.

### Build order rule

- **Notebooks 00–03 (first draft exception):** the notebooks already exist.
  Write the handbook chapters retroactively, referencing the notebooks as they
  stand today.
- **Notebook 04 onward:** write the notebook first, then the handbook chapter
  references it. Never write the handbook before the notebook.

### What not to do

- Do not write a second textbook. The handbook supports the notebook; it does
  not replace it.
- Do not let the handbook grow past 3× the notebook prose without a review.
- Do not add historical anecdotes, tangential theory, or advanced topics unless
  they directly help the learner understand the notebook material.
- Do not use "the learner" — address the reader as **you**, same as the
  notebooks.

---

## 4. Production sequence

The fastest way to build the notebook set is to work in layers.

### Layer A — curriculum design

- Freeze the notebook sequence.
- Assign each notebook one primary concept.
- Write the trainer goal for each notebook.
- Identify the required visuals and equations.

### Layer B — notebook skeletons

- Create all notebook files with headings only.
- Add placeholder markdown for objectives, steps, exercises, and recap.
- Add one empty code cell per planned computation or plot.

### Layer C — beginner-local helpers

- Create a small helper area directly under `beginner/` for reusable notebook
  code.
- Use this area for shared constants, plotting helpers, baseline calculations,
  and tiny radar-specific utilities that multiple notebooks need.
- Keep the helper surface narrow so each notebook still teaches its own logic.

### Layer D — shared assets

- Prepare a single shared import/setup cell pattern.
- Define the plotting style and labels once.
- Decide which helper functions are reused across notebooks and place them in
  the beginner-local helper area.
- Confirm all examples use the same baseline radar parameters.

### Layer E — content build

- Fill Notebook 0 and Notebook 1 completely.
- Validate the learner flow before continuing.
- Build Notebook 2 through Notebook 8 in dependency order.
- Finish with the integration notebook and portfolio artifact notebook.

### Layer F — trainer package

- Write trainer notes for each notebook.
- Add anticipated learner confusions.
- Add suggested timing and pacing.
- Add checkpoint answers and expected observations.

### Layer G — learner handbook

- Write handbook chapters that reference the completed notebooks.
- Each chapter opens with the same learning objectives.
- Walk through the concepts in narrative form with equations.
- Reference specific notebook cells; do not duplicate code or output.
- Close with expanded "closing the loop" answers.
- Check that the 2–3× prose ratio is respected.

### Layer H — quality pass

- Check that every notebook has a clear beginning, middle, and end.
- Check that every notebook teaches one new idea.
- Check that every notebook links back to the glossary and physics docs.
- Check that the trainer notes are enough to present the lesson without
  reverse-engineering the notebook.
- Check that every learner handbook chapter references the correct notebook cells
  and respects the 2–3× prose ratio.
- Check that the trainer guide references the learner handbook where deeper
  explanation is available.

---

## 5. Notebook-by-notebook plan

Each notebook below includes the learner goal, the notebook content, and the
trainer companion notes that should exist beside it.

### Notebook 0 — Radar intuition and baseline parameters

**Learner goal:** understand what pulse radar is and why the baseline
parameters were chosen.

**Must contain:**

- Pulse radar vs continuous wave intuition.
- Monostatic radar and the quiet listening interval.
- Duty cycle, PRI, PRF, and unambiguous range.
- Baseline parameter table with `f_c`, `B`, `τ`, `T`, `f_s`, `N`.
- One simple calculation for duty cycle and round-trip delay.

**Code cells should show:**

- Importing the beginner-local helper module if needed.
- Parameter loading.
- Duty-cycle calculation.
- Delay-to-range calculation.
- A simple timing diagram or annotated pulse plot.

**Trainer companion notes:**

- Lead with the “shout then listen” analogy.
- Emphasize that the baseline numbers are intentional, not arbitrary.
- Call out the aliasing teaching point: the 40 m/s target is chosen on
  purpose for later Doppler discussion.

### Notebook 1 — Pulse generation and chirp intuition

**Learner goal:** see how a rectangular pulse becomes an LFM chirp and why
chirps improve range resolution.

**Must contain:**

- Rectangular pulse generation.
- LFM chirp generation.
- Frequency sweep from start to stop frequency.
- Time-bandwidth product intuition.
- Plain-pulse range resolution vs chirp range resolution.

**Code cells should show:**

- Importing any shared helper used for pulse generation or plotting.
- Pulse and chirp waveforms in time.
- Instantaneous frequency or a frequency sweep plot.
- A matched-filter compression preview.

**Trainer companion notes:**

- Explain that the learner is still building the transmit waveform, not the
  full radar chain yet.
- Keep the physics simple: energy spread in time, resolution gained through
  bandwidth.

### Notebook 2 — Channel model and echoes

**Learner goal:** understand how a transmitted pulse becomes a delayed,
attenuated, noisy echo.

**Must contain:**

- Range to delay conversion.
- One-target channel model.
- Noise and attenuation.
- Optional second target as a stretch exercise.
- A visual echo versus transmit waveform comparison.

**Code cells should show:**

- Importing a beginner-local delay or plotting helper if used.
- Propagation delay in samples.
- Echo placement in the received signal.
- Noise addition.
- A plot of transmit pulse, echo, and noisy receive signal.

**Trainer companion notes:**

- Reuse the echo analogy from the physics doc.
- Stress that the learner is now seeing the physical meaning of delay.
- Keep the second target as an optional extension, not a required concept.

### Notebook 3 — Matched filtering and range estimation

**Learner goal:** understand correlation as matched filtering and convert a
peak delay into range.

**Must contain:**

- Correlation interpretation of the matched filter.
- Peak detection.
- Range from delay.
- Raw echo versus compressed output comparison.
- Why matched filtering beats thresholding the raw echo.

**Code cells should show:**

- Importing the shared matched-filter helper if used.
- Correlation of receive and transmit signals.
- The matched-filter output.
- Peak location.
- Range estimate.

**Trainer companion notes:**

- Pause on the idea that the filter is “looking for a known shape.”
- Use the plot to show why the compressed peak is the key improvement.

### Notebook 4 — Doppler and the range-Doppler map

**Learner goal:** understand fast time versus slow time and how Doppler turns
into velocity.

**Must contain:**

- Fast-time and slow-time explanation.
- Pulse stacking across a CPI.
- Slow-time FFT.
- Range-Doppler map axes.
- Velocity resolution and ambiguity.

**Code cells should show:**

- Importing any shared helper for stacking pulses or plotting maps.
- Multiple pulses with phase rotation.
- FFT across pulses.
- A range-Doppler heatmap.
- The baseline 40 m/s ambiguity case.

**Trainer companion notes:**

- Keep the distinction between delay and phase rotation explicit.
- Make the aliasing example deliberate and visible.
- This notebook should feel like the first major milestone.

### Notebook 5 — Kalman tracking

**Learner goal:** see how noisy detections become a stable track over time.

**Must contain:**

- State vector for range and velocity.
- Predict and update steps.
- Process noise and measurement noise.
- True versus measured versus tracked trajectories.
- One multi-target stretch example only if time allows.

**Code cells should show:**

- Measurement sequence.
- Prediction step.
- Update step.
- Track plot.

**Trainer companion notes:**

- Teach the Kalman filter as a balance between trust in the model and trust in
  the sensor.
- Do not over-mathematize the first pass; keep the plot central.

### Notebook 6 — Array geometry and beam patterns

**Learner goal:** understand how a ULA measures angle and why beam patterns
form main lobes and sidelobes.

**Must contain:**

- Element geometry.
- Steering vector definition.
- Phase offset formula.
- Beam pattern versus angle.
- Grating lobe discussion.

**Code cells should show:**

- Array geometry diagram.
- Steering vector values at a chosen angle.
- Beam pattern sweep.

**Trainer companion notes:**

- Use geometry language before matrix language.
- Keep the number of elements small so the pattern is easy to interpret.

### Notebook 7 — DOA and interference

**Learner goal:** compare Bartlett and Capon, then see how interference can
mask a target.

**Must contain:**

- Bartlett scan.
- Capon/MVDR idea.
- Two-close-target comparison.
- Strong interferer example.
- Before/after discussion of masking.

**Code cells should show:**

- Angle scan plots.
- A side-by-side Bartlett/Capon comparison.
- Interference impact on the target.

**Trainer companion notes:**

- Make the resolution difference visible, not just stated.
- Frame interference as a practical obstacle, not an abstract side case.

### Notebook 8 — Beam steering and adaptive nulling

**Learner goal:** understand how steering and LCMV nulling suppress an
interferer while preserving the target.

**Must contain:**

- Beam steering toward the target.
- LCMV constraint idea.
- Null depth at the interferer angle.
- Before/after beam patterns.
- Before/after range-Doppler maps.

**Code cells should show:**

- Target steering weights.
- Null-steering weights.
- Beam pattern with a deep null.
- RD map before and after cancellation.

**Trainer companion notes:**

- Explain why nulling happens before the matched filter.
- Emphasize that the target should remain visible after cancellation.

### Notebook 9 — Integration and portfolio artifacts

**Learner goal:** connect the full chain and produce the final artifacts.

**Must contain:**

- End-to-end overview of the full pipeline.
- Range-Doppler map artifact.
- Beam pattern artifact.
- Null pattern plus before/after artifact.
- GNU Radio comparison or preview if included later.

**Code cells should show:**

- End-to-end pipeline run.
- Artifact export or display.
- Short recap of where each notebook fits in the system.

**Trainer companion notes:**

- Use this notebook as the final story review.
- Ask the learner to explain the whole chain in their own words.

---

## 6. Trainer packet per notebook

Each notebook should have a companion trainer note page. The trainer packet
should be short but complete.

### Required trainer packet fields

- Notebook number and title.
- Lesson objective in one sentence.
- Prerequisites.
- 3 to 5 key talking points.
- Suggested pacing.
- What to demo live.
- Likely learner confusions.
- Checkpoint answer key.
- Optional stretch prompt.

### Suggested trainer flow

1. Start with the objective.
2. Define the one new concept.
3. Run the main plot or calculation.
4. Ask the checkpoint question.
5. Close with the takeaway and next notebook.

---

## 7. Notebook acceptance checklist

Before a notebook is considered done, check that:

- The learner goal is explicit.
- The notebook teaches one primary concept.
- The code cells are small and readable.
- The plots reinforce the lesson.
- The trainer notes are sufficient to present the notebook without guessing.
- The notebook references the physics and glossary docs where needed.
- The notebook ends with a recap and a checkpoint.

---

## 8. Fastest-path recommendation

If speed is the priority, do this first:

1. Draft this playbook fully.
2. Create notebook skeletons for all ten notebooks.
3. Write trainer notes for Notebook 0 through Notebook 4.
4. Fill Notebook 0 through Notebook 4.
5. Validate the learner flow.
6. Finish Notebook 5 through Notebook 9.
7. Add the extension-track notebook plan only after the spine is stable.

That gives you the shortest path to a complete teaching package without
revisiting the structure halfway through.

---

## 9. Publishing note (defer to the end)

Publish-to-web setup (for example GitHub Pages, Quarto, Jupyter Book, or an
nbconvert-based docs pipeline) should be done only after the notebook content
and trainer guide chapters are stable.

Why this is deferred:

- early setup creates repeated configuration churn while notebooks are changing,
- links, navigation, and chapter ordering will shift during development,
- and build tooling decisions are easier once the final notebook set is known.

When the beginner track is complete, add a final publishing stage:

1. Freeze notebook filenames and chapter order.
2. Choose the publishing toolchain.
3. Generate a browsable documentation site.
4. Add GitHub Pages deployment.
5. Verify that notebook links, Colab links, and trainer guide chapter links all work.
