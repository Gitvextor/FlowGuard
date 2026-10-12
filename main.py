"""Command-line entry point for the foundation demo or desktop UI."""

import argparse

from scripts.foundation_demo import main as foundation_main


def main() -> int:
    parser = argparse.ArgumentParser(description="FlowGuard Windows task companion")
    parser.add_argument("--ui", action="store_true", help="launch the PyQt6 dashboard")
    args = parser.parse_args()
    if args.ui:
        from app.ui import launch

        return launch()
    return foundation_main()


if __name__ == "__main__":
    raise SystemExit(main())
