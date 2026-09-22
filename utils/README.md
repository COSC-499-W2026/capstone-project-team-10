# Utils

> **This file is part of the documentation set.** Every markdown file in `docs/`, `tests/` and
> `utils/`, plus the root-level `README.md`, `AGENTS.md` and `CLAUDE.md`, is reviewed on every
> pull request and updated in the same PR when affected. Update this file whenever a utility
> scope folder is added, or the rule for what belongs here changes. See §9.0 of
> [the source of truth](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md).

Development and maintenance helpers that are **not** imported by the running application.

If `src/` imports it at runtime, it belongs in `src/`, not here. This directory is for scripts
and tools the team runs by hand: data inspection, DICOM dumping, config migration, mesh
diffing, build helpers, and the like.

## Layout rule, for humans and AI agents alike

**Every utility lives in a subfolder scoped to what it is for. Never put a loose utility file
at the root of `utils/`.**

The subfolder name mirrors the `src/` area the utility serves:

| Utilities for | Goes in |
|---|---|
| `src/windows/views/` | `utils/views/` |
| `src/windows/models/` | `utils/models/` |
| `src/classes/mesh/` | `utils/mesh/` |
| `src/classes/dicom/` | `utils/dicom/` |
| `src/classes/pdf/` | `utils/pdf/` |
| `src/settings/` | `utils/settings/` |
| nothing in particular, genuinely project-wide | `utils/common/` |

Create the subfolder if it does not exist yet. Add a row above when you create a new scope.

```
utils/
├── README.md
├── common/
├── dicom/
│   └── dump_plan_channels.py
├── mesh/
├── models/
├── pdf/
├── settings/
│   └── migrate_config_keys.py
└── views/
```

If you cannot decide which scope a utility belongs to, that is usually a sign it is doing two
things and should be split. `utils/common/` is for things that truly span the project, not a
dumping ground for the undecided.

## Writing a utility

- Give it a module docstring saying what it does and how to run it. A utility nobody can work
  out how to invoke is dead weight.
- Utilities import from `src/`, so they need `src/` on `sys.path`, the same as the app and the
  tests. Run them from the repository root.
- Utilities follow the same conda-only rule as everything else. Never `pip install` a
  dependency for a one-off script; add it to the environment properly or do without.
- A utility that touches patient data must not write DICOM, patient names, or IDs into the
  repository. The sample sets in `SI_C_D30 Brachify_Ex*/` are de-identified. Keep it that way.

## Related

- [AGENTS.md](../AGENTS.md) — repository layout conventions and working rules
- [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md) — the source of truth for how `src/` is organised
- [tests/README.md](../tests/README.md) — the same scoping rule, applied to tests
