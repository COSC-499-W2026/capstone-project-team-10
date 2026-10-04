import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def tracked_shell_scripts() -> list[str]:
    """Return the path of every *.sh file git tracks, relative to the repository root.

    A helper, not a test. It asks git rather than walking the folder, so untracked scratch
    scripts are ignored and only files a teammate would get from a clone are checked.
    """
    listing = subprocess.run(
        ["git", "ls-files", "*.sh"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return listing.stdout.splitlines()


def test_session_start_hook_is_a_tracked_shell_script() -> None:
    """Check that the session-start hook is among the shell scripts git tracks.

    Guards the line-ending test below. That test runs once per tracked script, so if the
    script list came back empty it would run zero times and pass without checking anything.
    """
    assert ".claude/hooks/session-start.sh" in tracked_shell_scripts()


@pytest.mark.parametrize("script", tracked_shell_scripts())
def test_shell_script_is_checked_out_with_lf_on_every_os(script: str) -> None:
    """Check that git checks each tracked shell script out with LF line endings on every OS.

    Asks git which eol attribute applies to the script, and expects "lf" from the *.sh rule
    in .gitattributes. Without it, Git for Windows defaults to core.autocrlf=true and checks
    the file out with CRLF. sh then fails on the first line with "$'\\r': command not found",
    and a broken session-start hook means the agent never sees the Session start steps in
    AGENTS.md.
    """
    attribute = subprocess.run(
        ["git", "check-attr", "eol", "--", script],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    assert attribute.stdout.strip() == f"{script}: eol: lf"
