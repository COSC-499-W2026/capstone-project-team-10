"""Exercise the slow marker that pytest.ini registers and tests/conftest.py applies."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

PLAN_IN_A_SHARED_WINDOW = "tests/views/test_remove_custom_needle.py::test_removing_an_unknown_label_raises_key_error_and_changes_nothing"
PLAN_IMPORTED_IN_THE_TEST = "tests/windows/test_main_window.py::test_export_button_is_enabled_after_a_plan_is_imported"
WINDOW_WITH_NO_PLAN = "tests/views/test_central_axis.py::test_axis_toggle_availability_and_preference"
SLOW_WITHOUT_A_WINDOW = "tests/pdf/test_template_reference.py::test_a_needle_leaving_a_dome_10_mm_off_axis_is_measured_from_the_dome"
PURE_LOGIC = "tests/dicom/test_data.py::test_reset_empties_every_field_that_init_declares"


def collected(marker_expression: str) -> set[str]:
    """Return the node IDs `python -m pytest -m <expression> --collect-only` selects. A helper, not a test.

    It runs a separate pytest, so the hook and pytest.ini are read exactly as a developer's
    command line reads them. An expression that selects nothing is an empty set, as pytest
    reports it with exit code 5. Fails with an AssertionError naming the exit code if that
    collection errors.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "-m", marker_expression],
        cwd=REPO_ROOT,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode in (pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED), result.stdout + result.stderr
    return {line for line in result.stdout.splitlines() if "::" in line}


@pytest.fixture(scope="module")
def quick_loop() -> set[str]:
    """Collect the quick loop, `-m "not slow"`, once for this file. A fixture, not a test."""
    return collected("not slow")


@pytest.mark.parametrize(
    "node_id",
    [PLAN_IN_A_SHARED_WINDOW, PLAN_IMPORTED_IN_THE_TEST, WINDOW_WITH_NO_PLAN, SLOW_WITHOUT_A_WINDOW],
)
def test_a_test_that_builds_a_window_or_takes_seconds_is_left_out_of_the_quick_loop(quick_loop: set[str], node_id: str) -> None:
    """Check `-m "not slow"` leaves out tests that build the main window, and the one slow test that does not.

    Fails if the hook stops labelling a window fixture, or the PDF test loses its own label.
    The quick loop would then import plans again and take minutes, so nobody would run it.
    """
    assert node_id not in quick_loop


def test_a_test_of_pure_logic_stays_in_the_quick_loop(quick_loop: set[str]) -> None:
    """Check a test that needs no window is still selected by `-m "not slow"`.

    Fails if the hook labels everything slow, which would leave the quick loop empty and
    every pure function untested between full runs.
    """
    assert PURE_LOGIC in quick_loop


def test_the_quick_loop_and_the_slow_tests_together_are_the_whole_suite(quick_loop: set[str]) -> None:
    """Check every collected test is in exactly one of `-m "not slow"` and `-m slow`.

    Fails if a marker expression drops tests, which would mean the plain `python -m pytest`
    a PR requires no longer runs what the two halves run.
    """
    assert quick_loop.isdisjoint(collected("slow"))
    assert quick_loop | collected("slow") == collected("")
