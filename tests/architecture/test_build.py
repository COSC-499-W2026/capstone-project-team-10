import importlib.util
from pathlib import Path

BUILD_PY = Path(__file__).resolve().parents[2] / "docs" / "architecture" / "build.py"
_spec = importlib.util.spec_from_file_location("architecture_build", BUILD_PY)
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)

# sha256 of b"flowchart LR\n  a --> b\n", the LF form a Mac or Linux checkout holds.
LF_SOURCE_SHA256 = "6f6b792eff678dab26795dffd124a9c0b854ffb58de4355be3142a7cad880be2"


def write_diagram(folder: Path, source: bytes) -> Path:
    mmd = folder / "flow.mmd"
    mmd.write_bytes(source)
    (folder / "flow.svg").write_text(f"<!-- source-sha256: {LF_SOURCE_SHA256} -->\n<svg></svg>\n")
    return mmd


def test_svg_is_current_when_source_is_checked_out_with_crlf(tmp_path: Path):
    # Git on Windows (core.autocrlf=true) checks the .mmd out with CRLF endings.
    # The same diagram must not read as stale, or --check blocks every Windows PR.
    mmd = write_diagram(tmp_path, b"flowchart LR\r\n  a --> b\r\n")

    assert build.svg_is_current(mmd) is True


def test_svg_is_stale_when_source_text_changed(tmp_path: Path):
    mmd = write_diagram(tmp_path, b"flowchart LR\n  a --> c\n")

    assert build.svg_is_current(mmd) is False
