# ZZ — Build Playbook (internal, temporary)

> **Internal tracker for us — not part of the learner-facing docs.** Delete
> this file once the full package below is complete. It exists so the overview
> can stay learner-facing instead of mixing in our build progress.

## Build progress

| Deliverable | Spec | Status |
|---|---|---|
| Docs tree | this repo | done |
| Python package `src/radar/` | `training/04-python-discipline.md` | pending |
| GNU Radio flowgraphs | `training/03-hardware.md` §2 | pending |
| Training resources (quizzes/labs/rubrics) | `training/06-training.md` | pending |

## Package parts (what "done" means)

1. **Docs** — `training/` tree (00–08 + README index). Complete.
2. **Python package** — `src/radar/` modules, CLI, pytest suite. Done when all
   test files in `training/04-python-discipline.md` §4 pass and every roadmap
   stage's verification is green.
3. **GNU Radio flowgraphs** — `radar_tx.grc`, `radar_rx_sim.grc`,
   `radar_doppler.grc` (+ array variant). Done when the
   `training/03-hardware.md` §5 validation checklist passes.
4. **Training resources** — quiz answers, lab solutions, rubrics. Done when
   `training/06-training.md` §3–§5 can be graded.

## Remove this file when

- [ ] All four parts are complete
- [ ] Build state is reflected in git history (commits + diffs)
- [ ] The learner-facing docs no longer reference build progress
