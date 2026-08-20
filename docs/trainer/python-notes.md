# Python Deep Dives (instructor-only)

Concept notes on the Python machinery the skeleton leans on. These are
lesson/slide material, deliberately kept *out* of the per-stage implementation
guides so each stage doc stays focused on the radar teaching. Each note links
back to the stage where the learner first hits the concept.

**Do not distribute to learners** — like the rest of `docs/trainer/`, these
notes assume the instructor context and the implementation-branch checkout.

## Dataclasses (`@dataclass`)

> **`@dataclass` = a function that reads your annotations and generates the
> boilerplate methods for you.** You write the data contract; it writes the
> plumbing. It does *not* extend a base class — `Target.__bases__` is just
> `(object,)`. The decorator reads each annotated field (`range_m: float`),
> generates `__init__`/`__repr__`/`__eq__` from them, and injects those methods
> straight into the class's own namespace (`__dict__`).

First encountered in **Stage 2** (`Target` in `src/radar/channel.py`).

### What a dataclass is

A learner seeing `Target` without an `__init__` may think the annotations are
globals or class attributes. They aren't — they're *annotations* the decorator
reads to decide what arguments the generated constructor takes and which
attributes it sets. The generated `__init__` is exactly the code you'd have
typed by hand:

```python
@dataclass
class Target:
    range_m: float
    velocity_mps: float
    angle_deg: float | None = None  # default -> optional kwarg
    snr_db: float = 20.0  # default -> optional kwarg
```

is equivalent to:

```python
class Target:
    def __init__(self, range_m, velocity_mps, angle_deg=None, snr_db=20.0):
        self.range_m = range_m
        self.velocity_mps = velocity_mps
        self.angle_deg = angle_deg
        self.snr_db = snr_db
```

### How and why we chose it

- The project convention is codified in `04-python-discipline.md` §2:
  *"Dataclasses for config and data objects (`Detection`, `State`)."* So
  `RadarConfig`, `Target`, and future `Detection`/`State` all follow one
  consistent pattern.
- `Target` is a **pure data carrier** — fields, no behavior. That is exactly
  what dataclasses are for.

### Why not the alternatives

| Option | Why we didn't use it |
|---|---|
| Plain class + handwritten `__init__` | Boilerplate; no `repr`/`eq` unless you also write those |
| `namedtuple` / `NamedTuple` | Immutable and tuple-based (positional access is awkward); adding mutable state or per-field defaults is clumsy |
| `attrs` (3rd-party) | Richer (validation, converters) but an extra dependency for no gain here |
| `pydantic` | Validation/serialization — heavy machinery for a teaching sim |
| ABC / `Protocol` ("interface" decorators) | Different job entirely: they define **behavior contracts** (`@abstractmethod`, `typing.Protocol` say "you must implement these methods"), not data layout. `Target` has no methods to contract |

### What the `dataclasses` stdlib module is for

The standard-library tool for classes that are mostly containers of data.
Declare the fields with annotations and defaults; the module generates the
plumbing (`__init__`, `__repr__`, `__eq__`, plus `__hash__`/`__lt__` with
`order=True`). Beyond the decorator itself:

- `field(default_factory=...)` — mutable defaults (lists/dicts)
- `frozen=True` — immutability
- `slots=True` — memory efficiency
- `asdict` / `astuple` / `replace` / `fields` — introspection and copying

### One-line summary

> **Dataclasses = "declare the data, get the boilerplate"; interfaces
> (ABC/Protocol) = "declare the behavior, make implementers obey."**
> `Target` needed the first, not the second.

---

## Decorators in this project

The skeleton uses only three decorators, and that restraint is itself a design
decision:

| Decorator | Where | Why it earns its place |
|---|---|---|
| `@dataclass` | `config.py`, `channel.py` | auto-generates boilerplate for data carriers (`RadarConfig`, `Target`) |
| `@property` | `tracker.py` (stage 7) | a computed, read-only value on a state object (e.g. derived `velocity_mps` from doppler bin) — no setter, so the value can't be mutated out of sync |
| `@pytest.fixture` | `tests/` | reusable, lazy test setup (e.g. the `cfg` fixture) |

### Why the others are avoided

- **`@abstractmethod` / ABCs** — a behavioral contract only pays off with
  inheritance hierarchies and multiple implementations (plugins, backends). This
  skeleton has exactly one implementation of each idea; an ABC would add an
  indirection layer and OO ceremony for zero teaching value. Learners are
  here to learn radar + disciplined NumPy, not design patterns.
- **`@staticmethod` / `@classmethod`** — only make sense when a function
  belongs to a class but doesn't need instance state. This codebase uses
  **module-level functions** (`signal_gen.lfm_chirp`, `channel.propagate`, ...):
  the *module itself is the namespace*, so a `@staticmethod` would just re-nest
  the same function behind a class for no benefit. On a data carrier like
  `Target`, a staticmethod that ignores `self` is a code smell.

  **A `@staticmethod` is never a capability** — it is a *stylistic grouping
  tool* (organize a helper under the class that owns it). Any staticmethod can
  be a module-level function instead. Prefer that here (or a shared `utils.py`
  for cross-cutting helpers); it is the same behavior with less nesting, and
  the function stays importable anywhere. Reach for a staticmethod only when a
  class genuinely *owns* the related behavior and would be the natural home —
  e.g. `datetime.utcfromtimestamp`, `np.random`-style factories, or a parser
  where `MyClass.from_format(...)` reads better. Our data carriers
  (`Target`, `RadarConfig`) never do, so you won't need staticmethods here.
- **`@classmethod`** — receives the **class** (`cls`) instead of an instance,
  so it can *create and return instances of that class*. Its main job is
  **alternative constructors / factories** — extra ways to build the same
  object:

  ```python
  @classmethod
  def stationary(cls, range_m, snr_db=20.0):
      return cls(range_m=range_m, velocity_mps=0.0, snr_db=snr_db)


  Target.stationary(1000.0)  # -> Target(range_m=1000.0, velocity_mps=0.0, ...)
  ```

  Using `cls` (not the literal class name) keeps the factory
  **inheritance-correct**: a subclass inherits it and still builds instances of
  the subclass. That is the one real advantage over a plain function. Standard
  examples everyone has used: `dict.fromkeys(iterable)`,
  `datetime.strptime(text, fmt)`, `int.from_bytes(bytes)` — "build one of me
  from something that isn't my normal constructor."

  **When you don't need it:** if every object is built one way via
  `ClassName(...)`, there is nothing to factor. That is exactly our case —
  `RadarConfig` and `Target` each have a single construction shape, so we skip
  classmethods entirely. Per the module-as-namespace rule, a second
  construction path would more likely be a module-level factory
  (`make_target_from_range(...)`) — though `@classmethod` is the idiomatic
  option when the factory naturally belongs on the class.

  **The three-way comparison at a glance:**

  | Kind | Receives | Typical use |
  |---|---|---|
  | instance method | `self` | uses per-object data (`target.range_m`) |
  | `@classmethod` | `cls` | alternative constructors / factories (`Target.stationary(...)`) |
  | `@staticmethod` | nothing | pure helper grouped under the class (conversion, validation) |
- **`@functools.cache` / `@lru_cache`** — the pure functions here are cheap and
  deterministic; caching adds hidden statefulness that fights the project's
  reproducibility discipline (fixed RNG seeds, `pytest` runnable headless). A
  cached result that outlives a changed seed is exactly the subtle bug we teach
  learners to avoid.
- **Third-party decorators** (`@pydantic` validators, `@attrs`, decorators for
  logging/metrics) — extra dependencies; `04-python-discipline.md` keeps the
  surface minimal so each stage teaches one radar concept.

**Rule of thumb for learners:** a decorator should *remove* boilerplate or
*enforce a rule* — if it's just nesting, skip it. The three above each do a
clear job: `@dataclass` writes the plumbing, `@property` enforces read-only
derived state, `@pytest.fixture` shares setup.