# ZZ — Build Playbook (internal, temporary)

> **Internal tracker for us — not part of the learner-facing docs.** Delete
> this file once the full package below is complete. It exists so the overview
> can stay learner-facing instead of mixing in our build progress.

## Build progress

| Deliverable | Spec | Status |
|---|---|---|
| Docs tree | this repo | done |
| Python package `src/radar/` | `training/04-python-discipline.md` | done (skeleton) |
| GNU Radio flowgraphs | `training/03-hardware.md` §2 | done (skeleton) |
| Training resources (quizzes/labs/rubrics) | `training/06-training.md` | done (trainer keys) |

## Package parts (what we delivered)

1. **Docs** — `training/` tree (00–08 + root README index). Complete.
2. **Python package** — `src/radar/` modules, CLI, pytest suite. **Delivered
   as skeleton**: all plumbing + `NotImplementedError` stubs committed,
   `ruff check` clean, `uv run pytest` collects the empty `tests/test_*.py`
   stubs (0 tests is the intended skeleton state). The learner-side "done"
   for the package is `04-python-discipline.md` (skeleton contract, §4) and
   the overall course DoD is `06-training.md` §9.
3. **GNU Radio flowgraphs** — `radar_tx.grc`, `radar_rx_sim.grc`,
   `radar_doppler.grc` (+ array variant). **Delivered as skeleton**: validated
   to generate and run under GRC 3.10; plumbing complete, the `radar_taps` /
   `doppler_phase` / `range_doppler` embedded Python blocks are learner
   stubs. Learner completion = the `training/03-hardware.md` §5 validation
   checklist (tied into `06-training.md` §9).
4. **Training resources** — quiz answers, lab solutions, rubrics committed
   under `docs/trainer/` (instructor-only). Delivered and usable: the
   `training/06-training.md` §5–§7 material can be graded from these keys.

## Remove this file when

- [ ] All four parts are complete
- [ ] Build state is reflected in git history (commits + diffs)
- [ ] The learner-facing docs no longer reference build progress
