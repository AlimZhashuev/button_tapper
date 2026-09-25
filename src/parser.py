import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запускает приложение на устройстве adb и нажимает кнопку заданного цвета."
    )
    parser.add_argument("package", help="Имя пакета")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path(__file__).with_name("config.yml"),
        help="Путь к YAML-конфигу",
    )
    parser.add_argument(
        "--color",
        help="Цвет кнопки: green, red, blue, yellow, orange, purple",
    )
    return parser.parse_args(argv)
