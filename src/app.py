import subprocess
import sys
import time

import cv2
import numpy as np
from loguru import logger

from config import AppConfig
from detector import Detector


class TapperApp:
    def __init__(self, config: AppConfig, detector: Detector) -> None:
        self.config = config
        self.detector = detector

    def run(self, package: str) -> int:
        self._check_device(package)
        while True:
            if not self._is_app_foreground(package):
                logger.warning(f"Приложение {package} завершило работу")
                return 0
            deadline = time.monotonic() + self.config.timeout_sec
            while time.monotonic() < deadline:
                image = self._screenshot()
                point = self.detector.find_button(image)
                if point is not None:
                    x, y = point
                    self._adb("shell", "input", "tap", str(x), str(y), timeout=5)
                    logger.debug(f"Кнопка цвета '{self.detector.color}' найдена и нажата: ({x}, {y})")
                    time.sleep(1.0)
                    break
                time.sleep(self.config.poll_interval_sec)

            else:
                logger.debug(
                    f"Кнопка цвета '{self.detector.color}' не найдена на экране приложения "
                    f"'{package}' за {self.config.timeout_sec:.0f} секунд."
                )
                time.sleep(1.0)

    def _run_adb(self, *args: str, timeout: float | None = None) -> subprocess.CompletedProcess[bytes]:
        try:
            return subprocess.run(
                ["adb", *args],
                capture_output=True,
                timeout=timeout or self.config.adb_timeout_sec,
            )
        except FileNotFoundError:
            sys.exit("adb не найден")
        except subprocess.TimeoutExpired:
            sys.exit(f"adb не ответил: adb {' '.join(args)}")

    def _adb(self, *args: str, timeout: float | None = None) -> bytes:
        result = self._run_adb(*args, timeout=timeout)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace").strip()
            sys.exit(f"adb ошибка ({result.returncode}): {err or ' '.join(args)}")
        return result.stdout

    def _screenshot(self) -> np.ndarray:
        raw = self._adb("exec-out", "screencap", "-p")
        image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            sys.exit("Не удалось получить скриншот с устройства.")
        return image

    def _check_device(self, package: str) -> None:
        if self._adb("get-state", timeout=5).decode().strip() != "device":
            sys.exit("Устройство не готово")

        launch = self._run_adb(
            "shell",
            "monkey",
            "-p",
            package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        )
        text = (launch.stdout + launch.stderr).decode("utf-8", errors="replace").lower()
        if launch.returncode != 0 or "no activities found" in text:
            sys.exit(f"Не удалось запустить '{package}'")

    def _is_app_foreground(self, package: str) -> bool:
        result = self._run_adb(
            "shell",
            "dumpsys",
            "activity",
            "activities",
            timeout=5,
        )

        if result.returncode != 0:
            return False

        text = (result.stdout + result.stderr).decode(
            "utf-8",
            errors="replace",
        )

        return package in text
