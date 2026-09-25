import cv2
import numpy as np

from config import DetectorConfig, hsv_ranges_for


class Detector:
    def __init__(self, config: DetectorConfig) -> None:
        self.color = config.color
        self.min_button_area = config.min_button_area
        self._ranges = [
            (
                np.array(
                    [r.h_low, r.s_low, r.v_low],
                    dtype=np.uint8,
                ),
                np.array(
                    [r.h_high, r.s_high, r.v_high],
                    dtype=np.uint8,
                ),
            )
            for r in hsv_ranges_for(config)
        ]

    def find_button(self, image: np.ndarray) -> tuple[int, int] | None:
        rect = self.find_button_rect(image)
        if rect is None:
            return None

        x, y, width, height = rect
        return x + width // 2, y + height // 2

    def find_button_rect(self, image: np.ndarray) -> tuple[int, int, int, int] | None:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for low, high in self._ranges:
            mask = cv2.bitwise_or(
                mask,
                cv2.inRange(hsv, low, high),
            )

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel,
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) < self.min_button_area:
            return None

        return cv2.boundingRect(contour)
