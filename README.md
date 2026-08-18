# active-radar-tracker-basics

An **active radar target tracker**: a pulse-Doppler radar simulation in Python
(NumPy/SciPy) and GNU Radio, with phased-array beamforming and adaptive
interference nulling. Sim-first — no hardware required; SDR hardware is
documented as an optional swap-in.

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