import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_PY = REPO_ROOT / "docs" / "architecture" / "build.py"

COMPLETE_DIAGRAM = (
    'ext["External"]\n'
    'state["Application state<br/>DicomModel, ShapeModel"]\n'
    'pres["Presentation<br/>Five views: Import, Export"]\n'
    'domain["Domain<br/>dicom: fileio, data<br/>mesh: cylinder, fileio<br/>pdf: canvas<br/>settings: load"]\n'
)


def load_build_module():
    """Import docs/architecture/build.py, which is a script and not an importable package.

    A helper, not a test. Loading it by path keeps the tests independent of sys.path.
    """
    spec = importlib.util.spec_from_file_location("architecture_build", BUILD_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str = "") -> None:
    """Create a file and any missing parent folders. A helper, not a test."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def tree(tmp_path: Path) -> dict:
    """Build a tiny src/ tree plus a diagram that names every module in it.

    Returns the src folder and the diagram path. Each test then adds one file the diagram does
    not name, so a failure points at exactly the rule that test is about.
    """
    src = tmp_path / "src"
    write(src / "classes" / "dicom" / "fileio.py")
    write(src / "classes" / "dicom" / "data.py")
    write(src / "classes" / "mesh" / "cylinder.py")
    write(src / "classes" / "mesh" / "fileio.py")
    write(src / "classes" / "mesh" / "__init__.py")
    write(src / "classes" / "pdf" / "canvas.py")
    write(src / "settings" / "load.py")
    write(src / "windows" / "models" / "dicom_model.py")
    write(src / "windows" / "models" / "shape_model.py")
    write(src / "windows" / "views" / "import_view.py")
    write(src / "windows" / "views" / "export_view.py")
    write(src / "windows" / "views" / "custom_view.py")
    mmd = tmp_path / "system-architecture.mmd"
    mmd.write_text(COMPLETE_DIAGRAM)
    return {"src": src, "mmd": mmd}


def test_drift_is_empty_when_the_diagram_names_every_module(tree: dict) -> None:
    """Check that a diagram naming every module reports no drift.

    Fails with a non-empty list if the check flags a module the diagram does name, or if it
    flags __init__.py or custom_view.py, which are deliberately not diagram entries. A false
    alarm here would block every commit that touches src/, and people would learn to ignore it.
    """
    build = load_build_module()
    assert build.drift(src=tree["src"], mmd=tree["mmd"]) == []


def test_drift_names_a_new_mesh_module(tree: dict) -> None:
    """Check that a new file in src/classes/mesh is reported until the mesh line names it.

    Fails with an empty list if the per-package line check is skipped. Then a new geometry
    module ships and the system architecture a reviewer reads silently omits it.
    """
    build = load_build_module()
    write(tree["src"] / "classes" / "mesh" / "intersections.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert problems == ["src/classes/mesh/intersections.py is not on the 'mesh:' line"]


def test_drift_names_a_new_package(tree: dict) -> None:
    """Check that a new folder under src/classes is reported when it has no line of its own.

    Fails with an empty list if only the files in known packages are compared. A whole new
    subsystem would then never appear in the system architecture.
    """
    build = load_build_module()
    write(tree["src"] / "classes" / "network" / "client.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert "package src/classes/network/ has no 'network:' line" in problems


def test_drift_names_each_file_in_a_new_package(tree: dict) -> None:
    """Check that a file inside a brand new src/classes package is reported as well as the package.

    Fails with only the package message if the per-file check covers a fixed list of package
    names. A new subsystem would then be flagged once, someone would add the bare package line,
    and every module inside it would still be missing from the diagram.
    """
    build = load_build_module()
    write(tree["src"] / "classes" / "network" / "client.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert problems == [
        "package src/classes/network/ has no 'network:' line",
        "src/classes/network/client.py is not on the 'network:' line",
    ]


def test_drift_names_a_new_model(tree: dict) -> None:
    """Check that a new *_model.py is reported until its CamelCase class name is in the diagram.

    Fails with an empty list if models are not compared. A new piece of application state
    would be invisible in the state layer of the diagram.
    """
    build = load_build_module()
    write(tree["src"] / "windows" / "models" / "navigation_model.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert problems == ["src/windows/models/navigation_model.py: NavigationModel is not named"]


def test_drift_names_a_new_view(tree: dict) -> None:
    """Check that a new *_view.py is reported until the view's name is in the diagram.

    Fails with an empty list if views are not compared. The diagram would claim five views
    when the app has six.
    """
    build = load_build_module()
    write(tree["src"] / "windows" / "views" / "tandem_view.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert problems == ["src/windows/views/tandem_view.py: Tandem is not named"]


def test_drift_does_not_match_a_module_name_on_another_package_line(tree: dict) -> None:
    """Check that a name on one package's line does not satisfy a different package.

    The diagram lists fileio under both dicom and mesh. Fails with an empty list if the check
    searches the whole diagram, because adding src/classes/pdf/fileio.py would then count as
    named just because other lines mention fileio.
    """
    build = load_build_module()
    write(tree["src"] / "classes" / "pdf" / "fileio.py")
    problems = build.drift(src=tree["src"], mmd=tree["mmd"])
    assert problems == ["src/classes/pdf/fileio.py is not on the 'pdf:' line"]


def test_the_real_system_architecture_names_every_module_in_src() -> None:
    """Check that docs/architecture/diagrams/system-architecture.mmd matches the real src/.

    Fails listing each unnamed module when someone adds a file without editing the diagram.
    This is the same check that build.py --check runs, so a stale diagram fails the test
    suite as well as the commit hook.
    """
    build = load_build_module()
    assert build.drift() == []
