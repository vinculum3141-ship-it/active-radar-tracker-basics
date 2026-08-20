# Trainer Materials (instructor-only)

Answer keys and grading guides for the learner-facing
`docs/training/06-training.md`. **Do not distribute these to learners** —
they contain quiz answers and milestone solutions. If learners receive this
repository directly, exclude or remove this directory first (e.g. keep it on
a branch or strip it for the learner checkout).

| File | Covers |
|---|---|
| `quiz-answers.md` | 06-training.md §5 weekly self-check quizzes (17 questions) |
| `lab-solutions.md` | 06-training.md §6 hands-on labs L1–L5 + common failure modes |
| `rubrics.md` | 06-training.md §7 verification rubrics with pass criteria and analytic truth |
| `implementation/` | Stage-by-stage implementation narrative for slides/lessons (see its README) |
| `python-notes.md` | Python deep dives kept out of the stage guides (dataclasses, etc.) |

The numeric answers are locked to the constants baked into the teaching
skeleton: `n_delay = 133` samples, `f_d = 653.3 Hz`, `v_max = 30.6 m/s`,
`Delta_v = 0.96 m/s`, CBF gain 4, LCMV null 40+ dB. Regenerate the array
numbers with `uv run grc/gen_weights.py`.

## How to run a session

1. Learner works the roadmap stage + self-check quiz for the week
   (06-training.md §4 objectives).
2. Grade the quiz with `quiz-answers.md`; accept ±5% where noted.
3. Assign the week's lab from §6; grade with `lab-solutions.md`.
4. Collect the milestone artifact; grade with `rubrics.md` (P / P- / R).
5. Any R → redo the milestone; its tests must pass again
   (04-python-discipline.md §4).