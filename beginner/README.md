# Beginner

[![Open GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Docs-2F6F5C?style=for-the-badge&logo=github)](https://vinculum3141-ship-it.github.io/active-radar-tracker-basics/)

This folder is the editable source for the beginner radar learning track. It contains the
notebooks, the learner and trainer narrative content, and the shared helper code.

The source-of-truth for course content lives here. The public docs site in `docs/` is a
separate publishing layer for GitHub Pages and should not be treated as the canonical place for
editing the learning materials.

Shared functionality used by multiple notebooks belongs in `beginner/helpers/`.

## The beginner radar story

This is the stable entry page for the beginner track. The story stays here so the learning flow
is not tied to a temporary draft document that may later be moved into a presentation.

The notebooks in this track tell one continuous story: a radar is built layer by layer, from a
simple pulse to a system that can detect a target, estimate its motion, sense its direction, and
reject interference.

The arc is intentionally staged. We begin with a pulse and the idea of measuring range by listening
for an echo. Once that timing problem is understood, the next step is signal design: why a chirp
is useful, how matched filtering increases sensitivity, and how the echo becomes a clear range
measurement. After that, the learner adds motion through Doppler processing and tracks the target
with a Kalman filter. The final stages move into spatial sensing and adaptive nulling, where the
radar learns angle and separates a desired signal from a stronger interferer.

The whole path is meant to feel like one coherent build: transmit a pulse, recover the echo,
estimate range and velocity, locate direction, and then keep the track stable in a noisy scene.

That is the learning arc behind the notebooks. The notebook itself is the lab, the learner guide
explains the reasoning, and the helper package keeps the code readable without hiding the physics.

## Published docs and supporting material

- [Helper scripts for beginner notebooks](../docs/helper-api.md) - documentation for the reusable helper functions
- [Learner guide](./learner_guide.md) - deeper conceptual explanations for the course
- [Publication roadmap](./publication-roadmap.md) - publication and rollout planning

## Suggested layout

- `beginner/helpers/` - reusable notebook helpers
- `beginner/00-*.ipynb` through `beginner/10-*.ipynb` - learner notebooks
- `beginner/learner_guide.md` - conceptual guide for self-paced study
- `beginner/09-playbook.md` - internal development notes and release planning
