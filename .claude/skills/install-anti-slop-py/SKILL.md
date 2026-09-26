---
name: install-anti-slop-py
description: Vendor and configure the anti-slop-py linter in a local Python repository. Use whenever a user asks to add anti-slop rules to a Python project, copy the anti-slop-py linter, ban Any/object/cast/type-ignore escape hatches, enforce evidence policy alongside Ruff and a type checker, or migrate an existing local anti-slop-py setup.
---

**This skill is deliberately not run in this repository.** Do not copy the linter into
`tools/anti_slop/`, and do not create or edit a `pyproject.toml` for it.

The linter is already vendored and runs from its source, with no install step:

```bash
PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils
```

If the request in front of you is to ban `Any`, `cast`, or another escape hatch in code you are
writing, apply the Anti-slop section of [AGENTS.md](../../../AGENTS.md#anti-slop) and run the
command above. That is the whole of it.

The install procedure, at
[agent-skills/anti-slop-py/skills/install-anti-slop-py/SKILL.md](../../../agent-skills/anti-slop-py/skills/install-anti-slop-py/SKILL.md),
changes how the whole team lints. Read it only if the user explicitly asks to install anti-slop
into this repository, and even then tell them it has deliberately not been run here (see
[agent-skills/README.md](../../../agent-skills/README.md)) and get their confirmation before
changing anything.
