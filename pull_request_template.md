_Enter PR description here... what is it supposed to do?_

---

## Part A: What I Built and Why I Know It Works

_These are the course's receipts for this PR. The same text is copied into the author's
individual log, `docs/logs/<student>/week-<K>.md`, and the two are kept identical. Replace
every `[...]` with the real answer in **bold**, keep one side of each "or", and delete the
italic guidance lines. Fill in every receipt whatever the PR changes, and mark one that cannot
apply **N/A** with a reason. Keep each answer to the shortest phrase that names its evidence,
and write nothing outside the template's own sentences. The rules are in
[docs/workflows/make-pr.md](docs/workflows/make-pr.md#fill-in-part-a)._

### For PR #**[number]**

- As part of requirement **[reference which requirement]**, the user needs to do
  **[enumerate sequence of actions in the system]**.
- Therefore, I implemented/generated code so that **[list functions supported for which
  intended user group]**.

_Include each of the next three subsections only if this PR changes code in its scope, and
delete it otherwise. Inside an included subsection keep every bullet, and mark one that does
not apply **N/A** with a reason._

#### Data Modeling and Integrity

- This data **[name]** is modeled as **[data type]** because **[reason]**. We considered
  alternative models such as **[explain details and why you did not go with them]**.
- This data **[name]** uses the input validation to ensure it adheres to **[indicate
  pattern]**.
- This data **[name]** may be vulnerable to **[security issue]**. Therefore, it uses a
  security-based sanitization by **[explain method taken]**. We considered alternative
  security solutions such as **[explain details and why you did not go with them]**.
- This data **[name]** may be vulnerable to **[privacy issue]**. Therefore, it uses a
  privacy-based sanitization by **[explain method taken]**. We considered alternative privacy
  solutions such as **[explain details and why you did not go with them]**.
- This data **[one or multiple names]** stores sensitive information and uses the encryption
  method **[name and describe approach]**. We considered alternative encryption methods such
  as **[explain details and why you did not go with them]**.
- The data **[name]** has access controls that restrict **[read or write]** privileges to the
  user group **[name of user group]**. We considered alternative privileges such as
  **[explain details and why you did not go with them]**.

#### Backend

- The system uses **[architectural pattern]** because **[relate to requirements and
  constraints that support your choice]**. Benefits for using this pattern include **[list
  with brief explanations with details to your project]**. Possible risks include **[list
  with brief explanations with details to your project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - We considered alternative solutions such as **[explain details and why you did not go
    with them]**.
  - _(Repeat for additional risks mitigated.)_
- The system architecture diagram consists of the following major components: **[list name
  and responsibility of each component]**. This structure has low coupling because
  **[provide detailed justification related to each component]**. This structure has high
  cohesion because **[provide detailed justification related to each component]**. This
  design is scalable because **[provide detailed rationale and use possible future
  requirements to illustrate scalability]**.

  **[provide diagram]**
- The system uses **[type of database]** database because **[reasons related to the type of
  data, relationships in the data, deployment needs, data compliance, or other technical
  factors]**. This method is done by **[explain steps in the implementation]**. Benefits for
  using this approach include **[list with brief explanations with details to your
  project]**. Possible risks include **[list with brief explanations with details to your
  project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - We considered alternative solutions such as **[explain details and why you did not go
    with them]**.
  - _(Repeat for additional risks mitigated.)_
- The system uses **[synchronous or asynchronous data processing]** because **[relate to
  requirements and constraints that support your choice]**. This method is done by
  **[explain steps in the implementation]**. Benefits for using this approach include
  **[list with brief explanations with details to your project]**. Possible risks include
  **[list with brief explanations with details to your project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - We considered alternative solutions such as **[explain details and why you did not go
    with them]**.
  - _(Repeat for additional risks mitigated.)_
- The system adopts a **[stateful or stateless]** approach to state management because
  **[relate to requirements and constraints that support your choice]**. This method is done
  by **[explain steps in the implementation]**. Benefits for using this approach include
  **[list with brief explanations with details to your project]**. Possible risks include
  **[list with brief explanations with details to your project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - We considered alternative solutions such as **[explain details and why you did not go
    with them]**.
  - _(Repeat for additional risks mitigated.)_
- The Level 0 DFD consists of the following major components: **[list name of each
  component]**. **[explain the interaction between the external entities and the system]**.

  **[provide diagram]**
- The Level 1 DFD consists of the following major processes: **[list name and responsibility
  of each process]**. **[trace the flow of this diagram using a happy path, specifying the
  input data, the processes triggered, access to data stores, and output for the target
  external entity]**. **[trace the flow of this diagram using a failure path, specifying the
  same types of information and explaining when errors arise and where they are handled]**.

  **[provide diagram]**
- The backend API must serve **[identify client and any relevant deployment constraints]**.
  We decided to use **[API architecture]** for all interactions with the backend because
  **[relate to requirements and constraints that support your choice]**. Benefits for using
  this approach include **[list with brief explanations with details to your project]**.
  Possible risks include **[list with brief explanations with details to your project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - _(Repeat for additional risks mitigated.)_
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **[traceability table enumerating each requirement
  and test PR IDs]**
- By using **[name of tool]** to check for test coverage, we found that our tests have
  **[percentage in number]** coverage because **[test runs and screenshot as proof]**.

#### Frontend

- The frontend uses **[approach to store, sync, and cache data]** received from the backend
  because **[relate to requirements and constraints that support your choice]**. Benefits for
  using this pattern include **[list with brief explanations with details to your
  project]**. Possible risks include **[list with brief explanations with details to your
  project]**.
  - To mitigate **[identify specific risk]**, we implemented **[details of solution taken]**.
  - _(Repeat for additional risks mitigated.)_
- The frontend ensures only authorized users **[specify user group]** can access restricted
  pages **[list the pages]** because **[relate to requirements and constraints that support
  your choice]**. Special guards put in place to ensure this include **[explain steps
  taken]**. Unauthorized access to **[list which pages]** will result in **[explain how the
  system handles the error and include the screenshot the unauthorized user sees]**.
  - _(Repeat for additional error types or unauthorized user groups.)_
- The frontend is designed using **[identify framework]** with design components for **[list
  of major groups of components used]**. Therefore, changing the design of **[pick one of
  your components]** will automatically change the look and feel of all instances of that
  component throughout the system. Changes to the content will not affect the design because
  **[explain how content and presentation are handled separately]**.
- The usability evaluation identified the following major problems: **[list major problems
  with brief descriptions]**. We categorized these as major because **[consequences if left
  unchanged]**. We resolved the problem **[identify major problem]** by doing **[specific
  steps taken]**. We considered alternative solutions such as **[explain details and why you
  did not go with them]**.
  - _(Repeat for additional major problems.)_
- The frontend adopts accessibility principle **[identify principle, reference, and brief
  description]**. The aspects that demonstrate this principle in the system include
  **[specify the relevant aspects and provide screenshots]**.
  - _(Repeat for additional accessibility principles adopted.)_
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **[traceability table enumerating each requirement
  and test PR IDs]**
- By using **[name of tool]** to check for test coverage, we found that our tests have
  **[percentage in number]** coverage because **[test runs and screenshot as proof]**.

#### Review and design

- When I reviewed the **[reference specific part(s) of generated code]** for this
  functionality, I did not find any problems with it because **[explain verification
  approach taken]**.

  _or_
- When I reviewed the **[reference specific part(s) of generated code]** for this
  functionality, I noticed **[identify problem details and why it is problematic]**.
  Therefore, I did **[explain solution taken]**.
  - _(Repeat for additional problems found.)_
- The PR does not contain any temporary workaround because **[explain adherence to long term
  solution or how the PR does not contain code logic]**.
- The PR only contains small functions that are **[number of lines]** long.
- I did **[specific steps taken]** to ensure that my feature contribution does not contain
  any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities

  _or_
- By doing **[explain specific steps]**, I found that my feature contribution contained
  **[identify which problem from the list below]**. Therefore, I did **[explain
  solution]**.
  - _(Repeat for additional problems found.)_

  Now, I can confirm that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- _(If applicable)_ The review by **[agent or teammate's name]** identified **[problem]**.
  Therefore, I did **[solution]**.
- This work is written in **[existing/new file name]** because **[architectural design
  reason]**.
- This work belongs in **[existing/new process name]** in the DFD because **[architectural
  design reason]**.

#### Testing receipts

_If the tests are in this PR, keep them under the heading above. If this is a test PR for
functionality merged in an earlier PR, replace the heading with "For test PR #**[number]**
written to assess functionality in **[PR# and brief description]**", and delete every
receipt above this subsection._

- The functionality works correctly because the happy path tests involving **[list of happy
  path tests]** passed.
- I wrote tests to cover abnormal situations involving **[list of abnormal tests]** and they
  passed.
- I checked that these negative cases involving **[list of negative tests]** failed as
  expected.
- When I reviewed the **[method name of generated test]**, I noticed **[problem details and
  why it is problematic]**. Therefore, I did **[explain solution taken]**.
  - _(Repeat for additional problems found.)_
- Among these tests, **[list of tests]** are unit tests and **[list of tests]** are
  integration tests.

  _or_
- Among these tests, **[list of tests]** are unit tests and integration tests are not
  required because **[modularity reason]**.
- These tests are included in the directory **[full path]**.
- This new test PR did not break anything else in the system because **[regression testing
  done and screenshot as proof]**.

  _or_
- This new test PR broke **[identify part of system impacted]** because **[explain conflict
  between new and existing code]**. Therefore, I did **[explain solution taken]**.
  - _(Repeat for additional problems found.)_

  Now, I can confirm that this test PR no longer breaks anything else in the system because
  **[regression testing done and screenshot as proof]**.

---

## Documentation gate

**The documentation set is updated in the same PR as the change it describes, never
afterwards.** The set is every markdown file the team owns, listed in §9.0 of
[the source of truth](docs/project/COSC499-TEAM10-PROJECT-DOCS.md). The code is the source of
truth: where a document disagrees with it, the document is wrong. Reviewing a file and
concluding it needs no change is fine. Not looking is not.

I reviewed each of these and updated the ones this PR affects:

- [ ] [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) — the source of truth (see section map below)
- [ ] [docs/project/COSC499-BRACHIFY-INIT-DOCS.md](docs/project/COSC499-BRACHIFY-INIT-DOCS.md) — the init guide to the inherited code. Not rewritten: any section this PR makes out of date gets a short note pointing to the new documentation
- [ ] [docs/README.md](docs/README.md) — index of the docs tree
- [ ] [docs/architecture/README.md](docs/architecture/README.md) — the diagrams match this PR, and `python docs/architecture/build.py --check` passes. That README says when they must be redrawn.
- [ ] [docs/contract/README.md](docs/contract/README.md)
- [ ] [docs/proposal/README.md](docs/proposal/README.md)
- [ ] [docs/design/README.md](docs/design/README.md)
- [ ] [docs/minutes/README.md](docs/minutes/README.md)
- [ ] [docs/logs/README.md](docs/logs/README.md)
- [ ] [docs/workflows/](docs/workflows/) — `README.md`, `commit.md`, `make-pr.md`
- [ ] [tests/README.md](tests/README.md) — TDD policy and the `tests/` scoping rule
- [ ] [utils/README.md](utils/README.md) — the `utils/` scoping rule
- [ ] [README.md](README.md) — repository entry point
- [ ] [AGENTS.md](AGENTS.md) — conventions, commands, architectural facts
- [ ] [CLAUDE.md](CLAUDE.md) — agent entry point
- [ ] [agent-skills/README.md](agent-skills/README.md) — the skill list. `sh .claude/hooks/session-start.sh`
      exits 0 and prints no `UNDOCUMENTED` or `STALE ROW` line
- [ ] [pull_request_template.md](pull_request_template.md) — this checklist
- [ ] [.claude/](.claude/) — `README.md`, `commands/*.md`, `skills/*/SKILL.md`

**If nothing in the set needed changing, say so explicitly here:**
_e.g. "Reviewed every file in the set; none affected, this PR only touches internal geometry helpers."_

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
- [ ] I did **not** edit any file inherited from upstream brachify (`README-BRACHIFY.md`,
      `pull_request_template_brachify.md`, `virtual_environments_instructions.md`, `notes/`,
      `user_guide/`, `3D Models and Templates/`, `Images/`, `LICENSE`, `requirements.txt`, the
      sample DICOM folders), or any vendored file inside a skill's folder in `agent-skills/`.
      `spec-file.txt` and `environment.yml` changed only if a dependency did, and then for
      Windows, macOS and Linux together, as §1.1 of the source of truth describes. See
      [AGENTS.md](AGENTS.md#what-is-ours-and-what-is-inherited).

**Which section of the source of truth applies:**

| If this PR... | Update |
|---|---|
| changes dependencies, the environment, or how to run the app | §1 Setup. A dependency follows the procedure in §1.1, for Windows, macOS and Linux together |
| adds, removes, or renames a module or file | §4.7 map **and** §5 module reference |
| changes signals, values, view order, a model, `ShapeModel`, the display path, or an export input or output | the diagrams in `docs/architecture/` (its README says how), and §4.4, §4.5 |
| adds or changes a view or widget | §4.3, §5.6 |
| adds or changes a `CONFIG_*` key | §6.2 (**and all four code sites**) |
| changes an export format | §6.4 |
| finds or fixes a bug | §7 Known bugs, traps and dead code |
| adds tests | §8, and every function in it has a docstring |
| adds, removes, or updates a skill in `agent-skills/` | the table in [agent-skills/README.md](agent-skills/README.md); §1.10 only if how skills load changes |

## Agent skills

Every AI agent that worked on this PR, in any tool, loads the skills in
[agent-skills/](agent-skills/) at the start of each session and applies them while it works.
See [AGENTS.md](AGENTS.md#session-start) and [agent-skills/README.md](agent-skills/README.md).
If no AI agent touched this PR, mark each item N/A.

- [ ] Every agent session loaded the superpowers `test-driven-development` skill before writing
      code. In Claude Code that is the plugin's copy, which the session-start hook prompts for.
      With any other agent, it read [agent-skills/superpowers-tdd/SKILL.md](agent-skills/superpowers-tdd/SKILL.md).
- [ ] Every agent session read each `SKILL.md` in `agent-skills/` and followed the ones that
      applied to the task. With an agent other than Claude Code, I confirmed it read `AGENTS.md`.
- [ ] If Python changed, `PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils`
      reports no blocking finding, and none was silenced with a suppression or a cast. See
      [AGENTS.md](AGENTS.md#anti-slop).

## Test-driven development

This project writes the test first. See
[AGENTS.md](AGENTS.md#testing-write-the-test-first).

- [ ] `python -m pytest` passes from the repository root.
- [ ] I wrote the test **before** the code.
- [ ] I **watched it fail**, then made it pass.
- [ ] I broke the code on purpose and confirmed the test caught it.
- [ ] Every test, helper and fixture I wrote has a docstring saying what it checks, how it
      fails, and why that matters, with no `#` comment repeating it. See
      [AGENTS.md](AGENTS.md#every-function-in-tests-explains-itself).
- [ ] The test lives in the correctly scoped subfolder (`tests/mesh/`, `tests/dicom/`, …) and
      not at the root of `tests/`. See [tests/README.md](tests/README.md).
- [ ] Logic that could not be tested was moved out of the view or model into a pure function
      and tested there, rather than covered by a test that only asserts nothing raised.
