_Enter PR description here... what is it supposed to do?_

---

## Documentation gate

**The documentation set is updated in the same PR as the change it describes, never
afterwards.** The set is every markdown file in `docs/`, `tests/` and `utils/`, plus the three
root-level files. Reviewing one and concluding it needs no change is fine. Not looking is not.

I reviewed each of these and updated the ones this PR affects:

- [ ] [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) — the source of truth (see section map below)
- [ ] [docs/README.md](docs/README.md) — index of the docs tree
- [ ] [docs/contract/README.md](docs/contract/README.md)
- [ ] [docs/proposal/README.md](docs/proposal/README.md)
- [ ] [docs/design/README.md](docs/design/README.md)
- [ ] [docs/minutes/README.md](docs/minutes/README.md)
- [ ] [docs/logs/README.md](docs/logs/README.md)
- [ ] [docs/workflows/](docs/workflows/) — `README.md`, `commit.md`, `make-pr.md`
- [ ] [tests/README.md](tests/README.md) — the `tests/` scoping rule
- [ ] [utils/README.md](utils/README.md) — the `utils/` scoping rule
- [ ] [README.md](README.md) — repository entry point
- [ ] [AGENTS.md](AGENTS.md) — conventions, commands, architectural facts
- [ ] [CLAUDE.md](CLAUDE.md) — agent entry point

**If nothing in the set needed changing, say so explicitly here:**
_e.g. "Reviewed all 12; none affected, this PR only touches internal geometry helpers."_

Quality of the updates:

- [ ] I read the relevant sections **before** starting, not after.
- [ ] Anything I wrote is marked *Verified* (observed at runtime) or *Reasoned from code*
      — I did not silently promote the second to the first.
- [ ] Cross-references stayed consistent. If I changed a rule stated in more than one file,
      I updated every copy.
- [ ] Any new bug or trap I found is written into **§7 Known bugs, traps and dead code** of
      [the source of truth](docs/project/COSC499-TEAM10-PROJECT-DOCS.md#7-known-bugs-traps-and-dead-code),
      not left in a PR comment where it will be lost.
- [ ] If I **fixed** a bug already listed in that §7 catalogue, I marked the entry as fixed
      rather than deleting it, so a future reader can still see the trap once existed.
- [ ] I did **not** edit upstream's inherited files (`README-BRACHIFY.md`,
      `virtual_environments_instructions.md`, `pull_request_template_brachify.md`, `notes/`).

**Which section of the source of truth applies:**

| If this PR... | Update |
|---|---|
| changes dependencies, the environment, or how to run the app | §1 Setup |
| adds, removes, or renames a module or file | §4.7 map **and** §5 module reference |
| changes signals, models, or the display pipeline | §4.4, §4.5 |
| adds or changes a view or widget | §4.3, §5.6 |
| adds or changes a `CONFIG_*` key | §6.2 (**and all four code sites**) |
| changes an export format | §6.4 |
| finds or fixes a bug | §7 Known bugs, traps and dead code |
| adds tests | §8 |

## Tests

See [AGENTS.md](AGENTS.md#testing).

- [ ] The test lives in the correctly scoped subfolder (`tests/mesh/`, `tests/dicom/`, …) and
      not at the root of `tests/`. See [tests/README.md](tests/README.md).
- [ ] Logic that could not be tested was moved out of the view or model into a pure function
      and tested there, rather than covered by a test that only asserts nothing raised.

## Change checklist

- [ ] Branched off `main`; merged latest `main` into this branch.
- [ ] **No AI attribution anywhere** in my commits or in this description. No
      `Co-Authored-By` trailer, no "Generated with" line, no model or tool name.
- [ ] Any user-facing copy I wrote or changed contains **no em dash and no colon**
      (dialogs, `.ui` strings, PDF text, the import info panel). See
      [AGENTS.md](AGENTS.md#ui-copy).
- [ ] I ran the app and exercised the affected path — not just "it imports".
- [ ] Sample data still imports: `SI_C_D30 Brachify_Ex1/` (and `Ex2/` if this touches the
      tandem, since only `Ex2` has a `Tandem` channel).
- [ ] If I touched geometry, I visually inspected the Export tab for malformed channels.
- [ ] If I edited a `.ui` file, I regenerated its `*_ui.py` with `pyside6-uic` and did **not**
      hand-edit the generated file.
- [ ] If I touched the DICOM readers, I considered whether the other vendor branch
      (Varian ↔ Nucletron) needs the mirror fix.
- [ ] If I added a dependency, I used conda (never `pip`) and regenerated `spec-file.txt`
      with `conda list --explicit > spec-file.txt`.
- [ ] No secrets, patient data, or PHI added. Sample DICOM is de-identified — keep it that way.

## Review

- [ ] Self-reviewed the full diff for anything unintended.
- [ ] Reviewer assigned.

**Reviewer:**

- [ ] Merged latest `main` into the branch and **ran the code**.
- [ ] Verified every documentation-set file the change touches matches what the code now
      does, and that the author either updated them or stated that none were affected.
- [ ] Read through the changed files for anything weird or unintended.
- [ ] Comments are sufficient and not excessive; no typos; professional.
- [ ] Approved.

---

_Upstream brachify's own review process is preserved in
[`pull_request_template_brachify.md`](pull_request_template_brachify.md). Use it for PRs going
back to the `upstream` remote, which also require Michael Kudla's review and merge._
