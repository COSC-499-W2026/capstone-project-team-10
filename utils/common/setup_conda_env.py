"""Create the brachify conda environment for this machine's OS.

Prints the conda create command by default. Pass ``--run`` to execute it.
Requires conda on PATH. Never uses pip.

    python -m utils.common.setup_conda_env
    python -m utils.common.setup_conda_env --name brachify --run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from utils.common.conda_env import conda_create_argv

REPO_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    """CLI flags for dry-run versus create."""
    parser = argparse.ArgumentParser(
        description=(
            'Build or run the conda create command for brachify. '
            'Windows uses spec-file.txt; macOS and Linux use conda-forge packages.'
        ),
    )
    parser.add_argument(
        '--name',
        default='brachify',
        help='conda environment name (default: brachify)',
    )
    parser.add_argument(
        '--run',
        action='store_true',
        help='run conda create (default: print the command only)',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Print or run the OS-specific conda create command. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        command = conda_create_argv(
            platform=sys.platform,
            env_name=args.name,
            repo_root=REPO_ROOT,
        )
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    printable = ' '.join(command)
    if not args.run:
        print(printable)
        print(
            'Dry run only. Re-run with --run to create the environment.',
            file=sys.stderr,
        )
        return 0
    if shutil.which('conda') is None:
        print('conda was not found on PATH. Install Miniforge or Anaconda first.', file=sys.stderr)
        return 1
    print(printable)
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


if __name__ == '__main__':
    raise SystemExit(main())
