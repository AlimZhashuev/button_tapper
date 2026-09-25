from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints

import yaml

T = TypeVar("T")


@dataclass
class HsvConfig:
    h_low: int = 35
    s_low: int = 70
    v_low: int = 70
    h_high: int = 85
    s_high: int = 255
    v_high: int = 255


COLOR_HSV: dict[str, list[HsvConfig]] = {
    "green": [HsvConfig(35, 70, 70, 85, 255, 255)],
    "red": [
        HsvConfig(0, 70, 70, 10, 255, 255),
        HsvConfig(170, 70, 70, 179, 255, 255),
    ],
    "blue": [HsvConfig(90, 70, 70, 130, 255, 255)],
    "yellow": [HsvConfig(20, 70, 70, 35, 255, 255)],
    "orange": [HsvConfig(10, 70, 70, 22, 255, 255)],
    "purple": [HsvConfig(130, 70, 70, 160, 255, 255)],
}


@dataclass
class DetectorConfig:
    color: str = "green"
    min_button_area: int = 1500
    hsv: list[HsvConfig] | None = None


@dataclass
class AppConfig:
    timeout_sec: float = 10.0
    poll_interval_sec: float = 0.4
    adb_timeout_sec: float = 15.0
    detector: DetectorConfig = field(default_factory=DetectorConfig)


def hsv_ranges_for(config: DetectorConfig) -> list[HsvConfig]:
    if config.hsv is not None:
        return config.hsv
    color = config.color.lower()
    if color not in COLOR_HSV:
        known = ", ".join(COLOR_HSV)
        raise ValueError(f"Неизвестный цвет '{config.color}'. Доступны: {known}.")
    return COLOR_HSV[color]


def _unwrap_type(ftype: Any) -> Any:
    origin = get_origin(ftype)
    if origin in (Union, UnionType):
        non_none = [arg for arg in get_args(ftype) if arg is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return ftype


def _from_dict(cls: type[T], data: dict[str, Any] | None) -> T:  # noqa
    if not data:
        return cls()
    kwargs: dict[str, Any] = {}
    hints = get_type_hints(cls)
    for f in fields(cls):
        if f.name not in data:
            continue
        value = data[f.name]
        ftype = _unwrap_type(hints.get(f.name, f.type))
        origin = get_origin(ftype)
        args = get_args(ftype)
        if origin is list and args and is_dataclass(args[0]):
            items = value if isinstance(value, list) else [value]
            kwargs[f.name] = [_from_dict(args[0], item) if isinstance(item, dict) else item for item in items]
        elif is_dataclass(ftype) and isinstance(value, dict):
            kwargs[f.name] = _from_dict(ftype, value)
        else:
            kwargs[f.name] = value
    return cls(**kwargs)


def load_config(path: Path | None) -> AppConfig:
    if path is None or not path.is_file():
        return AppConfig()
    try:
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Некорректный YAML в конфиге {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"Конфиг {path} должен быть YAML-словарём")
    return _from_dict(AppConfig, raw)
