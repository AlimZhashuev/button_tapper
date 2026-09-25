import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).parent.parent.parent
MAIN_SCRIPT = PROJECT_DIR / "src" / "main.py"

PACKAGE = "com.example.buttontest"


@pytest.fixture
def adb_device() -> None:
    result = subprocess.run(
        ["adb", "get-state"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    if result.returncode != 0 or result.stdout.strip() != "device":
        pytest.skip("Android-устройство не подключено")


@pytest.mark.e2e
def test_button_tapper_e2e(adb_device: None) -> None:
    process = subprocess.Popen(
        [
            sys.executable,
            str(MAIN_SCRIPT),
            PACKAGE,
        ],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        time.sleep(5)
    finally:
        process.terminate()

        try:
            output, _ = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            output, _ = process.communicate()

    assert "найдена и нажата" in output, f"Кнопка не была нажата {output}"
