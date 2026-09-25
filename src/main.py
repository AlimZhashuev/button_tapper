import sys

from app import TapperApp
from config import load_config
from detector import Detector
from parser import parse_args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    conf = load_config(args.config)
    if args.color:
        conf.detector.color = args.color
        conf.detector.hsv = None
    try:
        detector = Detector(conf.detector)
    except ValueError as exc:
        sys.exit(str(exc))

    app = TapperApp(conf, detector)
    return app.run(args.package)


if __name__ == "__main__":
    sys.exit(main())
