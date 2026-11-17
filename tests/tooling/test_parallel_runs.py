"""Exercise the pytest-xdist dependency that lets the suite run its test files in parallel."""
from __future__ import annotations

import re
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_DOCS = REPO_ROOT / "docs" / "project" / "COSC499-TEAM10-PROJECT-DOCS.md"


def macos_create_command() -> str:
    """Return the `conda create` command in §1.2 of the project docs. A helper, not a test.

    Fails with StopIteration if §1.2 no longer has a `conda create -n brachify` block, so the
    test using it cannot pass by reading nothing.
    """
    blocks = re.findall(r"```bash\n(.*?)```", PROJECT_DOCS.read_text(encoding="utf-8"), re.DOTALL)
    return next(block for block in blocks if "conda create -n brachify" in block)


@pytest.mark.parametrize(
    "listed",
    [
        pytest.param(lambda: (REPO_ROOT / "environment.yml").read_text(encoding="utf-8"), id="environment.yml"),
        pytest.param(lambda: (REPO_ROOT / "spec-file.txt").read_text(encoding="utf-8"), id="spec-file.txt"),
        pytest.param(macos_create_command, id="macos-linux-command"),
    ],
)
def test_pytest_xdist_is_listed_wherever_the_environment_is_defined(listed: Callable[[], str]) -> None:
    """Check pytest-xdist is named in environment.yml, the Windows lockfile and the §1.2 command.

    Fails if any of the three drops it. §1.1 of the project docs requires every dependency on
    Windows, macOS and Linux together, so a teammate built from the list missing it would get
    "unrecognized arguments: -n" from the documented parallel command and fall back to the
    ten-minute serial run.
    """
    assert re.search(r"(^|[\s/-])pytest-xdist([\s=-]|$)", listed(), re.MULTILINE)


def test_pytest_xdist_is_installed_in_this_environment() -> None:
    """Check the xdist plugin can be imported in the environment running the tests.

    Fails if the conda environment was built without pytest-xdist, which means it was not
    made from the files the test above checks, so `python -m pytest -n auto` cannot run here.
    """
    assert find_spec("xdist") is not None
