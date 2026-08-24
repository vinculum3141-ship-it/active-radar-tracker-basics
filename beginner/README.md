# Beginner

This folder contains the standalone learner notebooks and any shared helper
code they need.

Rules:
- Notebooks here must run independently.
- Notebooks may not import from `src/radar/`.
- Shared functionality used by multiple notebooks belongs in `beginner/_shared/`.
- Notebook code should import only from standard scientific Python packages and
  beginner-local helpers.

Suggested layout:

- `beginner/_shared/` - reusable notebook helpers
- `beginner/00-*.ipynb` through `beginner/09-*.ipynb` - learner notebooks
- `beginner/09-playbook.md` - trainer build plan
