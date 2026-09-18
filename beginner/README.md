# Beginner

This folder is the editable source for the beginner radar learning track. It contains the
notebooks, the learner and trainer narrative content, and the shared helper code.

The source-of-truth for course content lives here. The public docs site in `docs/` is a
separate publishing layer for GitHub Pages and should not be treated as the canonical place for
editing the learning materials.

Shared functionality used by multiple notebooks belongs in `beginner/helpers/`.

## Published docs and supporting material

- [Helper scripts for beginner notebooks](../docs/helper-api.md) - documentation for the reusable helper functions
- [Learner guide](./learner_guide.md) - deeper conceptual explanations for the course
- [Trainer guide](./trainer_guide.md) - instructor-facing notes and delivery flow
- [Publication roadmap](./publication-roadmap.md) - publication and rollout planning

## Suggested layout

- `beginner/helpers/` - reusable notebook helpers
- `beginner/00-*.ipynb` through `beginner/10-*.ipynb` - learner notebooks
- `beginner/trainer_guide.md` - trainer guide with chapter notes
- `beginner/learner_guide.md` - learner guide with deeper explanations
- `beginner/09-playbook.md` - trainer build plan
