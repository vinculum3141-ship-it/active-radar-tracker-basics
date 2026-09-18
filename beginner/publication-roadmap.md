# Beginner notebook and publication roadmap

This document defines the sequence for moving from a compliant beginner notebook
track to a publishable docs experience. The goal is not just to "make it pretty";
the goal is to make the learning path readable, reusable, and easy to follow for
new learners.

## Goal

Create a beginner-friendly radar learning track that is:

- concept-first,
- mathematically explicit,
- calculation-heavy where it helps novices,
- consistent across all notebooks,
- backed by a coherent helper API,
- and ready to publish as a docs site or static learning portal.

## Current status

The beginner track is now in the publication-prep stage. The main remaining work
is to:

1. make the helper package self-describing,
2. document the publication structure in a concrete way,
3. scaffold a docs build that matches the learner flow,
4. publish only after the notebooks and guides are stable.

## Phase 0 — define the learner-facing standard

Before publishing anything, every notebook must meet the following requirement set:

- readable for beginners,
- includes the necessary math and physics,
- shows the calculation in explicit cells,
- repeats the implementation in a helper-backed form,
- uses a consistent structure chapter-to-chapter,
- runs successfully in the local environment and in Colab,
- ends with a recap or checkpoint that reinforces the physical idea.

## Phase 1 — align the notebook flow

### Notebook hard requirements for each chapter

Each notebook should contain the following sequence:

1. Title and learning goals.
2. A plain-language explanation of the concept.
3. Baseline values or setup.
4. The relevant equation(s).
5. A hand-worked calculation cell.
6. A helper-backed implementation cell.
7. A visual or numerical output.
8. A short learner checkpoint or common-mistake note.
9. A final summary connecting the concept to the broader radar story.

### Notebook pass list

- [x] 00-radar-intuition.ipynb
- [x] 01-pulse-chirp-intuition.ipynb
- [x] 02-radar-equation.ipynb
- [x] 03-channel-model-echoes.ipynb
- [x] 04-matched-filter-range.ipynb
- [x] 05-doppler-range-doppler.ipynb
- [x] 06-kalman-tracking.ipynb
- [x] 07-array-geometry-beam-patterns.ipynb
- [x] 08-doa-and-interference.ipynb
- [x] 09-beam-steering-adaptive-nulling.ipynb
- [x] 10-integration-artifacts.ipynb

## Phase 2 — tighten the helper API and documentation

The shared helper package is the bridge between the notebooks and the eventual docs site. It should be documented in the same tone as the learner material: explicit, simple, and tied to the underlying physics.

### Required helper documentation work

- [ ] Review each helper module for clear docstrings.
- [ ] Add module-level explanations for the beginner audience.
- [ ] Document formulas and assumptions for every shared function.
- [ ] Add short example usage snippets for the most common helpers.
- [ ] Ensure helper names and outputs are consistent with the notebook notation.
- [ ] Create a simple API reference section for the helper package.

### Primary files to review

- [beginner/helpers/__init__.py](../beginner/helpers/__init__.py)
- [beginner/helpers/constants.py](../beginner/helpers/constants.py)
- [beginner/helpers/math.py](../beginner/helpers/math.py)
- [beginner/helpers/waveforms.py](../beginner/helpers/waveforms.py)
- [beginner/helpers/channel.py](../beginner/helpers/channel.py)
- [beginner/helpers/doppler.py](../beginner/helpers/doppler.py)
- [beginner/helpers/array.py](../beginner/helpers/array.py)
- [beginner/helpers/doa.py](../beginner/helpers/doa.py)
- [beginner/helpers/steering.py](../beginner/helpers/steering.py)
- [beginner/helpers/kalman.py](../beginner/helpers/kalman.py)
- [beginner/helpers/plotting.py](../beginner/helpers/plotting.py)

## Phase 3 — create the publication docs layer

This phase starts after the notebooks and helper package are stable. At this point the docs become the learner's navigation system.

### Document types to create

- [ ] a beginner overview page,
- [ ] a learner guide landing page,
- [ ] a helper API reference page,
- [ ] a chapter index page for notebooks 00 through 10,
- [ ] a publishable home page with narrative and learning outcomes.

### Recommended publication stack

The simplest and most maintainable option for this repository is:

1. MkDocs + Material for MkDocs for the site,
2. Markdown and notebook reference pages for the learning narrative,
3. a light API section for the beginner helper package,
4. GitHub Pages deployment from the built docs output.

### Recommended site structure

- Home: project overview and learning outcomes
- Beginner track: chapter list and narrative flow
- Learner guide: conceptual explanations and chapter checkpoints
- Helper API: module overview and common usage patterns
- Publication notes: roadmap, build steps, and release checklist

## Phase 4 — publish and validate

- [ ] Generate the docs site locally.
- [ ] Verify all links and notebook references.
- [ ] Validate the publication build.
- [ ] Publish to GitHub Pages or the chosen hosting target.
- [ ] Confirm the learner-facing pages match the notebook flow.
- [ ] Archive a final release note and version tag.

## Recommended working order

1. Finish the helper docs pass.
2. Scaffold the docs site.
3. Add the learner-facing pages.
4. Validate the local MkDocs build.
5. Publish only after the site matches the course flow.

## Final publication exit criteria

The beginner track is ready to publish when:

- all notebooks meet the compliance standard,
- the helper API is documented,
- the docs site builds successfully,
- the published pages reflect the beginner experience accurately,
- and the learner can navigate from overview to notebook to helper reference without confusion.
