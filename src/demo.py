from pathlib import Path

import cv2
from loguru import logger

from config import DetectorConfig
from detector import Detector

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def main() -> None:
    detector = Detector(
        DetectorConfig(
            color="green",
            min_button_area=1500,
        )
    )

    image_dir = Path("/Users/alim/vk_test_project/vk_test/button_tapper/src/fixtures/images")
    image_paths = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)

    if not image_paths:
        logger.warning(f"В папке {image_dir} нет изображений.")
        return

    for image_path in image_paths:
        image = cv2.imread(str(image_path))

        if image is None:
            logger.error(f"Не удалось открыть: {image_path}")
            continue

        rect = detector.find_button_rect(image)
        if rect is None:
            logger.debug(f"{image_path.name}: кнопка не найдена")

            cv2.putText(
                image,
                "Button not found",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
        else:
            x, y, width, height = rect
            center_x = x + width // 2
            center_y = y + height // 2

            logger.debug(f"{image_path.name}: кнопка найдена ({center_x}, {center_y})")

            cv2.rectangle(
                image,
                (x, y),
                (x + width, y + height),
                (0, 0, 255),
                3,
            )

            cv2.circle(
                image,
                (center_x, center_y),
                8,
                (255, 0, 0),
                -1,
            )

            cv2.putText(
                image,
                f"Button: ({center_x}, {center_y})",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Button Tapper Demo", image)
        key = cv2.waitKey(0) & 0xFF
        if key in (ord("q"), 27):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
