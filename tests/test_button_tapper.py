from pathlib import Path
from unittest.mock import patch

import cv2
import pytest
from loguru import logger

from app import TapperApp
from config import AppConfig, DetectorConfig
from detector import Detector

IMAGE_DIR = Path(__file__).parent.parent / "src" / "fixtures" / "images"


@pytest.fixture
def detector() -> Detector:
    return Detector(
        DetectorConfig(
            color="green",
            min_button_area=1500,
        )
    )


@pytest.mark.parametrize(
    ("image_name", "button_expected"),
    [
        ("button_green_classic.jpeg", True),
        ("button_green_triangular.png", True),
        ("button_purple.png", False),
        ("green_button_4.png", True),
    ],
)
def test_find_green_button(
    image_name: str,
    button_expected: bool,
    detector: Detector,
) -> None:
    image = cv2.imread(str(IMAGE_DIR / image_name))
    assert image is not None

    point = detector.find_button(image)
    if button_expected:
        assert point is not None, f"Кнопка не найдена: {image_name}"
        x, y = point
        logger.debug(f"{image_name}: кнопка найдена: ({x}, {y})")
    else:
        assert point is None, f"Найдена кнопка: {image_name}"

def test_unknown_color() -> None:
    config = DetectorConfig(color="pink")

    with pytest.raises(ValueError, match="Неизвестный цвет"):
        Detector(config)

def test_timeout(detector):
    ...

def test_find_button_below_min_area(detector):
    ...