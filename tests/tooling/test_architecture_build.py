import importlib.util
from pathlib import Path

BUILD_PY = Path(__file__).resolve().parents[2] / "docs" / "architecture" / "build.py"

# sha256 of b"flowchart LR\n  a --> b\n", the LF form a Mac or Linux checkout holds.
LF_SOURCE_SHA256 = "6f6b792eff678dab26795dffd124a9c0b854ffb58de4355be3142a7cad880be2"


def load_build_module():
    """Import docs/architecture/build.py, which is a script and not an importable package.

    A helper, not a test. Loading it by path keeps the tests independent of sys.path.
    """
    spec = importlib.util.spec_from_file_location("architecture_build", BUILD_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_diagram(folder: Path, source: bytes) -> Path:
    """Write flow.mmd with the given bytes, beside an SVG stamped with LF_SOURCE_SHA256.

    A helper, not a test. Returns the .mmd path, ready for svg_is_current().
    """
    mmd = folder / "flow.mmd"
    mmd.write_bytes(source)
    (folder / "flow.svg").write_text(f"<!-- source-sha256: {LF_SOURCE_SHA256} -->\n<svg></svg>\n")
    return mmd


def test_svg_is_current_when_source_is_checked_out_with_crlf(tmp_path: Path) -> None:
    """Check that an unchanged diagram checked out with CRLF line endings counts as current.

    Fails with False if build.py hashes the raw bytes. Git for Windows defaults to
    core.autocrlf=true and checks every .mmd out with CRLF, so the hash never matches a stamp
    written on macOS or Linux, and build.py --check blocks every pull request from Windows.
    """
    build = load_build_module()
    mmd = write_diagram(tmp_path, b"flowchart LR\r\n  a --> b\r\n")
    assert build.svg_is_current(mmd) is True


def test_svg_is_stale_when_source_text_changed(tmp_path: Path) -> None:
    """Check that a diagram whose text changed counts as stale.

    Fails with True if line-ending normalisation hides a real edit. A stale SVG would then
    pass build.py --check, and the picture a reviewer reads would not match its source.
    """
    build = load_build_module()
    mmd = write_diagram(tmp_path, b"flowchart LR\n  a --> c\n")
    assert build.svg_is_current(mmd) is False
