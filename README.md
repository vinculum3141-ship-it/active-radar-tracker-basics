# active-radar-tracker-basics

[![Open GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Docs-2F6F5C?style=for-the-badge&logo=github)](https://vinculum3141-ship-it.github.io/active-radar-tracker-basics/)

An **active radar target tracker**: a pulse-Doppler radar simulation in Python
(NumPy/SciPy) and GNU Radio, with phased-array beamforming and adaptive
interference nulling. Sim-first — no hardware required; SDR hardware is
documented as an optional swap-in.

## Beginner notebook quick path

If you are starting with the beginner learning track, use this order:

1. Start with the beginner orientation in [beginner/README.md](beginner/README.md).
2. Read the deeper conceptual explanations in [beginner/learner_guide.md](beginner/learner_guide.md).
3. Run the matching notebook files in [beginner/notebooks](beginner/notebooks).
4. Use the helper reference in [docs/helper-api.md](docs/helper-api.md) when you want the notebook-support API quick lookup.

The notebooks remain the primary lab experience. The beginner guide explains the "why", and the helper docs provide the fast reference for the small support functions used in the examples.

## Docs

| Doc | What it covers |
|---|---|
| [00 — Overview](docs/training/00-overview.md) | Vision, skill domains, system diagram, radar parameters |
| [01 — Physics](docs/training/01-physics.md) | The science: range, matched filtering, chirp, Doppler, tracking, arrays, nulling |
| [02 — Architecture](docs/training/02-architecture.md) | Python + GNU Radio design, data contracts, sim↔hardware abstraction |
| [03 — Hardware & GNU Radio](docs/training/03-hardware.md) | GNU Radio install, flowgraphs, SDR swap-in map, legality |
| [04 — Python Discipline](docs/training/04-python-discipline.md) | Code spec: layout, module APIs, conventions, tests |
| [05 — Roadmap](docs/training/05-roadmap.md) | 5-week / 12-stage implementation plan with verifications |
| [06 — Training](docs/training/06-training.md) | Objectives, quizzes, labs, rubrics, portfolio artifacts |
| [07 — Glossary](docs/training/07-glossary.md) | Terms + key equations quick reference |
| [08 — Extensions](docs/training/08-extensions.md) | Elective specialization tracks: automotive, counter-drone, airport surveillance |

**Start with [00 — Overview](docs/training/00-overview.md).** Follow
[05 — Roadmap](docs/training/05-roadmap.md) to implement, using
[04 — Python Discipline](docs/training/04-python-discipline.md) as the code spec and
[06 — Training](docs/training/06-training.md) as you learn.

## License

See [LICENSE](LICENSE).