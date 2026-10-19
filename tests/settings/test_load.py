"""Exercise src/settings/load.py: reading a saved config file back into brachify's settings."""
from pathlib import Path

from settings.defaults import DEFAULT_CONFIG_VALUES
from settings.load import load_config_file


def load_from_text(tmp_path: Path, text: str) -> tuple[dict, list, int]:
    """Helper, not a test. Write text to a config file and load it with no configs loaded yet.

    Passes a copy of the defaults as the fallback, as brachify does at start-up, so a test can
    tell which values came from the file and which from the defaults.
    """
    config_file = tmp_path / "config.json"
    config_file.write_text(text, encoding="utf-8")
    return load_config_file(str(config_file), dict(DEFAULT_CONFIG_VALUES), 0)


def test_partial_file_loads_its_keys_and_reports_the_rest_missing(tmp_path: Path) -> None:
    """Check that a file with one key loads it and fills every other key from the defaults.

    Fails if the cylinder diameter in the file is not used, if the missing collar height is not
    the default 0.0 or not reported missing, or if the file is not counted as loaded. FR-CN-13
    requires a config without collar keys to fall back to defaults and report them, so the user
    is told which settings did not come from their file.
    """
    values, keys_loaded, configs_loaded = load_from_text(
        tmp_path, '{"CONFIG_CYLINDER_DIAMETER": 25.0}'
    )
    assert values["CONFIG_CYLINDER_DIAMETER"] == 25.0
    assert values["CONFIG_BASE_HEIGHT"] == 0.0
    assert keys_loaded[0] == ["CONFIG_CYLINDER_DIAMETER"]
    assert "CONFIG_BASE_HEIGHT" in keys_loaded[1]
    assert configs_loaded == 1


def test_unreadable_file_falls_back_to_defaults(tmp_path: Path) -> None:
    """Check that a file that is not valid JSON gives the defaults and is not counted as loaded.

    Fails if the broken file raises, loads any key, or increments the count. A half-saved or
    hand-edited config must not stop brachify from starting or be reported as loaded.
    """
    values, keys_loaded, configs_loaded = load_from_text(tmp_path, '{"CONFIG_CYLINDER_DIAM')
    assert values["CONFIG_CYLINDER_DIAMETER"] == 30.0
    assert keys_loaded[0] == []
    assert configs_loaded == 0


def test_true_is_not_accepted_as_a_dimension(tmp_path: Path) -> None:
    """Check that a JSON true for the cylinder diameter is rejected and the default 30.0 used.

    Fails if true is reported as loaded. Python treats True as the integer 1, so without this
    rule the cylinder is built 1 mm wide while the user is told their setting loaded, and a
    device of the wrong size could be printed for the patient.
    """
    values, keys_loaded, configs_loaded = load_from_text(
        tmp_path, '{"CONFIG_CYLINDER_DIAMETER": true}'
    )
    assert values["CONFIG_CYLINDER_DIAMETER"] == 30.0
    assert keys_loaded[0] == []
    assert configs_loaded == 0
