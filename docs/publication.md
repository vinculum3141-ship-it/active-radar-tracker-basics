# Publication plan

This project is structured as a learner-facing radar course with a clear split
between:

- the notebook-driven learning path,
- the conceptual companion guide,
- and the reusable helper package.

## Publication goals

The published site should help a learner do the following:

1. start from a clear overview,
2. understand the sequence of the notebooks,
3. read the conceptual companion when a notebook raises a question,
4. use the helper package as a reference without losing the physics narrative,
5. follow the same progression in a published, browsable format.

## Recommended structure

- Home page: project overview and radar story
- Beginner track: chapter list and notebook narrative
- Learner guide: conceptual explanations and checkpoint summaries
- Helper API: the shared functions and their purpose

## Build status

The site is intentionally kept simple and publication-friendly:

- no hidden assumptions about a complex build toolchain,
- markdown-first content,
- consistent chapter names across notebooks and docs,
- assistant-guided publication flow that mirrors the learner progression.

## Release checklist

Before publishing, confirm that:

- all notebook files are in the final sequence,
- the learner guide is complete and consistent,
- the helper package has clear docstrings,
- all links between chapters and docs are valid,
- the local MkDocs build passes without warnings.
