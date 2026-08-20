# Trainer — Implementation Guidance (stage-by-stage)

Instructor-only narrative of *how* the skeleton was implemented, written live
as each roadmap stage is built. Each file covers one stage and is written in
two layers:

- **Technical** — the physics, design decisions, code walkthrough, and key
  numbers a presenter can quote verbatim.
- **Plain-English** — the "In one sentence" summary and the takeaway bullets,
  for explaining the stage to a non-technical audience or as slide text.

These files exist to be mined for presentation slides and narrative lessons —
each section is deliberately structured so it can be lifted into a slide
deck or a lesson script.

## Files

| Stage | File |
|---|---|
| 1 · Radar waveform | `stage-01-waveform.md` |
| 2 · Moving target simulation | `stage-02-channel.md` |
| 3 · Range estimation (matched filter) | `stage-03-receiver.md` |
| 4 · Doppler / velocity (range-Doppler) | `stage-04-doppler.md` |
| 5 · Kalman tracking | `stage-05-tracker.md` |
| 6 · 4-element antenna array | `stage-06-array.md` |
| 7 · Direction-of-arrival | `stage-07-doa.md` |
| 8 · Interference source | `stage-08-interference.md` |
| 9 · Beam steering | `stage-09-beam-steering.md` |
| 10 · Adaptive null (LCMV) | `stage-10-lcmv.md` |
| 11 · Range-Doppler after cancellation | `stage-11-cancellation.md` |
| 12 · GNU Radio flowgraphs | `stage-12-gnuradio.md` |

## Running the tests

Each stage's Verification section lists its green commands. To watch tests pass
one by one (useful when demoing or debugging a stage), run the verbose form:

```bash
uv run pytest tests/test_signal_gen.py -v
```

Run the whole suite (all stages) with:

```bash
uv run pytest -v
uv run ruff check .
```

To run a single test (useful when debugging one behavior; the name after the
double colon is the test function):

```bash
uv run pytest tests/test_signal_gen.py::test_lfm_chirp_sweeps_bandwidth -v
```

## Stage template

Every stage file uses the same sections so the deck structure stays
consistent:

1. **In one sentence** — plain-English summary (non-technical audience).
2. **The problem** — *why* this stage exists: what we're trying to solve,
   in narrative terms, and what the deliverable is.
3. **Approach — the algorithm in words** — a readable, step-by-step recipe
   of how we solve it, *before any code*. Traceable to the code below.
4. **What we built** — the roadmap objective restated, plus a mapping of
   each algorithm step → the function that realizes it.
5. **Physics in play** — the science exercised, with the key equations.
6. **Design decisions** — choices made and why, including options rejected.
7. **Implementation** — detailed walkthrough with high-level code snippets.
8. **Key numbers** — the analytic truth to quote (test-independent).
9. **Verification** — what passed and which plot/criterion proves it.
10. **Gotchas / stretch notes** — aliasing, mis-tuning, extension ideas.
11. **Slide-ready takeaway** — 2–3 bullets usable verbatim on a slide.