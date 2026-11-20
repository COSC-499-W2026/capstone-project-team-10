"""Tests for the conda environment create-command builder."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.tooling.test_parallel_runs import macos_create_command

REPO_ROOT = Path(__file__).resolve().parents[2]


def packages_named_in_section_12() -> tuple[str, ...]:
    """Return the named packages in the §1.2 ``conda create -n brachify`` command, in order.

    A helper, not a test. Fails with StopIteration if that create line is missing, or
    AssertionError if no package lines follow it.
    """
    block = macos_create_command()
    lines = block.splitlines()
    start = next(
        index
        for index, line in enumerate(lines)
        if line.lstrip().startswith("conda create -n brachify")
    )
    packages: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if packages:
                break
            continue
        if stripped.startswith("conda ") or stripped.startswith("python "):
            break
        package = stripped.rstrip("\\").strip()
        if package:
            packages.append(package)
        if not stripped.endswith("\\"):
            break
    assert packages
    return tuple(packages)


def packages_named_in_environment_yml() -> frozenset[str]:
    """Return dependency names from environment.yml, without ``pip``. A helper, not a test."""
    names: set[str] = set()
    in_dependencies = False
    for line in (REPO_ROOT / "environment.yml").read_text(encoding="utf-8").splitlines():
        if line.startswith("dependencies:"):
            in_dependencies = True
            continue
        if not in_dependencies:
            continue
        if line and not line[0].isspace() and not line.startswith("-"):
            break
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        name = stripped[2:].strip()
        if name == "pip" or name.startswith("pip=") or not name:
            continue
        names.add(name)
    return frozenset(names)


def test_windows_create_uses_the_spec_file_and_never_pip() -> None:
    """Windows must create from spec-file.txt, not an unpinned solve or pip.

    A command that omits --file, points at the wrong path, or includes pip
    install fails. Newcomers on Windows who use the wrong path get a broken
    environment, and pip into conda is a known breakage here.
    """
    from utils.common.conda_env import conda_create_argv

    command = conda_create_argv(
        platform='win32', env_name='brachify', repo_root=REPO_ROOT,
    )
    assert command[:4] == ['conda', 'create', '--name', 'brachify']
    assert '--file' in command
    spec = Path(command[command.index('--file') + 1])
    assert spec == REPO_ROOT / 'spec-file.txt'
    assert 'pip' not in ' '.join(command).lower()
    assert '-c' not in command


def test_macos_create_names_every_section_11_package() -> None:
    """macOS must name every §1.1 package on conda-forge, with the two pins.

    Missing pyside6 or the pythonocc pin, or falling back to the Windows
    lockfile, fails. Apple Silicon matplotlib does not pull PySide6, so an
    incomplete list leaves launch.py unable to import Qt.
    """
    from utils.common.conda_env import conda_create_argv

    command = conda_create_argv(
        platform='darwin', env_name='brachify', repo_root=REPO_ROOT,
    )
    assert command[:3] == ['conda', 'create', '-n']
    assert command[3] == 'brachify'
    assert command[command.index('-c') + 1] == 'conda-forge'
    assert 'python=3.12' in command
    assert 'pythonocc-core=7.7.2' in command
    for package in (
        'pyside6', 'matplotlib', 'numpy', 'scipy', 'scikit-image',
        'reportlab', 'pydicom', 'pyinstaller', 'pytest', 'pytest-xdist',
    ):
        assert package in command
    assert '--file' not in command
    assert 'pip' not in ' '.join(command).lower()


def test_linux_create_matches_the_macos_package_list() -> None:
    """Linux uses the same named packages as macOS, never the win-64 lockfile.

    A Linux command that differs from darwin or uses spec-file.txt fails.
    The lockfile's binaries are Windows-only.
    """
    from utils.common.conda_env import conda_create_argv

    darwin = conda_create_argv(
        platform='darwin', env_name='brachify', repo_root=REPO_ROOT,
    )
    linux = conda_create_argv(
        platform='linux', env_name='brachify', repo_root=REPO_ROOT,
    )
    assert linux == darwin
    assert '--file' not in linux


def test_unknown_platform_is_refused() -> None:
    """An unsupported platform must raise before any conda command is built.

    Returning a guessed command would install the wrong binaries. Fail with
    ValueError so the CLI can print a clear message instead.
    """
    from utils.common.conda_env import conda_create_argv

    with pytest.raises(ValueError, match='platform'):
        conda_create_argv(
            platform='freebsd', env_name='brachify', repo_root=REPO_ROOT,
        )


def test_custom_env_name_is_passed_through() -> None:
    """The env name argument must appear in the create command on every OS.

    Hard-coding brachify would force every teammate onto one name and break
    people who keep a second test environment.
    """
    from utils.common.conda_env import conda_create_argv

    windows = conda_create_argv(
        platform='win32', env_name='brachify-test', repo_root=REPO_ROOT,
    )
    unix = conda_create_argv(
        platform='darwin', env_name='brachify-test', repo_root=REPO_ROOT,
    )
    assert windows[3] == 'brachify-test'
    assert unix[3] == 'brachify-test'


def test_unix_create_packages_match_section_12_and_environment_yml() -> None:
    """UNIX_CREATE_PACKAGES must stay identical to §1.2 and to environment.yml minus pip.

    Fails if a package is added to the docs or environment.yml but not the tuple, or the
    reverse. §1.1 lists four places that must agree; without this check the one-command
    create on macOS and Linux silently omits a new dependency.
    """
    from utils.common.conda_env import UNIX_CREATE_PACKAGES

    assert UNIX_CREATE_PACKAGES == packages_named_in_section_12()
    assert frozenset(UNIX_CREATE_PACKAGES) == packages_named_in_environment_yml()
