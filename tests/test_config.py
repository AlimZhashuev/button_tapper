from pathlib import Path

from config import load_config


def test_load_missing_config() -> None:
    config = load_config(Path("does_not_exist.yml"))

    assert config.timeout_sec == 10.0

def test_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        """
timeout_sec: 5
poll_interval_sec: 0.2
detector:
  color: blue
  min_button_area: 500
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.timeout_sec == 5
    assert config.poll_interval_sec == 0.2
    assert config.detector.color == "blue"
    assert config.detector.min_button_area == 500