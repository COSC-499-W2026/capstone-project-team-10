#!/bin/sh
# SessionStart hook for Claude Code, registered in .claude/settings.json.
#
# Claude Code adds whatever this prints to stdout to the session's context, on startup,
# resume, /clear and compaction. It lists every skill under agent-skills/ by reading each
# SKILL.md's frontmatter, so a skill added there is picked up with no change here.
#
# The rules themselves live in AGENTS.md, section "Session start". This script only
# makes Claude Code act on them before its first reply.

project_dir=${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}

# Fail loudly. Printing nothing would look like a clean session start with no instructions,
# and the make-pr check that looks for warnings in this output would pass.
if ! cd "$project_dir" 2>/dev/null; then
  echo "session-start.sh: cannot enter the project directory '$project_dir'." >&2
  echo "The agent-skills and TDD steps in AGENTS.md, section \"Session start\", were not shown." >&2
  exit 1
fi
if [ ! -f AGENTS.md ] || [ ! -d agent-skills ]; then
  echo "session-start.sh: '$project_dir' is not the repository root (no AGENTS.md or agent-skills/)." >&2
  echo "The agent-skills and TDD steps in AGENTS.md, section \"Session start\", were not shown." >&2
  exit 1
fi

# Prints one frontmatter field of a SKILL.md, e.g. `name` or `description`.
frontmatter_field() {
  awk -v key="$2" '
    NR == 1 && $0 == "---" { inside = 1; next }
    inside && $0 == "---" { exit }
    inside && index($0, key ":") == 1 {
      sub("^" key ":[ ]*", "")
      print
      exit
    }
  ' "$1"
}

cat <<'EOF'
Session start for capstone-project-team-10. AGENTS.md, section "Session start", requires
the following before your first reply of this session, in this order.

1. Invoke the superpowers:test-driven-development skill with the Skill tool, and follow it
   for the whole session. The repo-specific rules are in AGENTS.md, section
   "Testing: write the test first". If the Skill tool does not list that skill, the
   superpowers plugin is not installed on this machine. Read the vendored copy at
   agent-skills/superpowers-tdd/SKILL.md instead, tell the user, and point them to
   section 1.10 of docs/project/COSC499-TEAM10-PROJECT-DOCS.md.

2. Read the SKILL.md of every repository skill listed below, in full, now. They are
   vendored in agent-skills/. Then read agent-skills/README.md: its table says how each
   skill is used in this repository, and a note there (such as "deliberately not run")
   binds you. Follow a skill's procedure when its description matches the task in front
   of you and that table does not say otherwise. Do not run a procedure just because it is
   listed. To add a skill, follow "Adding a skill" in agent-skills/README.md.
EOF

skills=$(find agent-skills -name SKILL.md -not -path '*/node_modules/*' 2>/dev/null | sort)
index=agent-skills/README.md
if [ -z "$skills" ]; then
  echo "   (agent-skills/ holds no SKILL.md files.)"
else
  printf '%s\n' "$skills" | while IFS= read -r skill; do
    echo "   - $(frontmatter_field "$skill" name), at $skill"
    echo "     $(frontmatter_field "$skill" description)"
    # The table in agent-skills/README.md links each skill by its path under agent-skills/.
    if ! grep -qF "(${skill#agent-skills/})" "$index" 2>/dev/null; then
      echo "     UNDOCUMENTED: no row in $index. Do not follow its procedure yet."
      echo "     Tell the user, ask how this repository should use it, and add the row as"
      echo "     \"Adding a skill\" in $index describes, in the current change."
    fi
  done
fi

# A row whose SKILL.md no longer exists is a skill that was removed without its row.
grep -oE '\([^()]*SKILL\.md\)' "$index" 2>/dev/null | tr -d '()' | sort -u |
  while IFS= read -r row; do
    if [ ! -f "agent-skills/$row" ]; then
      echo "   - STALE ROW: $index lists agent-skills/$row, which does not exist. Tell"
      echo "     the user, and remove the row as \"Updating or removing a skill\" describes."
    fi
  done

cat <<'EOF'

3. Apply the Anti-slop section of AGENTS.md to every line of Python you write. After you
   edit Python, and before you say the work is done, run the check it names:
   PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils

4. Keep the documentation set in step with the code as you work. The code is the source of
   truth. Before any pull request, check every file in the set against the branch diff and
   update what the change made stale, in the same PR. The set, and the upstream files that
   must never be edited, are in AGENTS.md, section "You must update the documentation set".
EOF
