"""Build the conda create command for brachify on the current OS.

Windows uses the pinned lockfile ``spec-file.txt``. macOS and Linux name every
package from §1.1 of the project docs on conda-forge. Never uses pip.

Run from the repository root (default is print only; pass ``--run`` to create):

    python -m utils.common.setup_conda_env
    python -m utils.common.setup_conda_env --run
"""

from __future__ import annotations

from pathlib import Path

# Named packages for macOS and Linux. Keep in step with §1.1 and environment.yml.
# Only python and pythonocc-core carry versions.
UNIX_CREATE_PACKAGES: tuple[str, ...] = (
    'python=3.12',
    'pythonocc-core=7.7.2',
    'pyside6',
    'matplotlib',
    'numpy',
    'scipy',
    'scikit-image',
    'reportlab',
    'pydicom',
    'pyinstaller',
    'pytest',
    'pytest-xdist',
)

_WINDOWS = frozenset({'win32', 'cygwin'})
_UNIX = frozenset({'darwin', 'linux'})


def conda_create_argv(
    *,
    platform: str,
    env_name: str,
    repo_root: Path,
) -> list[str]:
    """Return argv for ``conda create`` for this OS. Does not run conda.

    ``platform`` is a ``sys.platform`` value (``win32``, ``darwin``, ``linux``).
    Raises ``ValueError`` for anything else so the CLI can refuse instead of
    guessing Windows or Unix packages.
    """
    if not env_name or env_name != env_name.strip():
        raise ValueError('env_name must be a non-empty name without surrounding spaces')
    if platform in _WINDOWS:
        spec = (repo_root / 'spec-file.txt').resolve()
        return ['conda', 'create', '--name', env_name, '--file', str(spec)]
    if platform in _UNIX:
        return [
            'conda', 'create', '-n', env_name, '-c', 'conda-forge',
            *UNIX_CREATE_PACKAGES,
        ]
    raise ValueError(
        f'Unsupported platform {platform!r}. Use win32, darwin, or linux.',
    )
