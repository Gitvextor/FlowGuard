"""Interactive acceptance demo for FlowGuard's Windows context engine."""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.context import ContextMonitor, EventDetector, WindowsContextProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show stable Windows App/title changes and event-triggered screenshots."
    )
    parser.add_argument(
        "--task",
        default="Complete the operating-systems Priority Scheduling lab",
    )
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--debounce", type=float, default=1.5)
    parser.add_argument(
        "--required-triggers",
        type=int,
        default=3,
        help="Stable events required for the acceptance PASS line.",
    )
    parser.add_argument(
        "--own-title",
        action="append",
        default=["FlowGuard"],
        help="Exact FlowGuard window title to exclude; may be repeated.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.required_triggers < 1:
        raise SystemExit("--required-triggers must be at least 1")
    provider = WindowsContextProvider(own_window_titles=args.own_title)
    monitor = ContextMonitor(
        provider,
        EventDetector(args.debounce),
        poll_interval_seconds=args.poll_interval,
    )
    monitor.set_task(args.task)

    print("=== FlowGuard Windows Context Demo ===")
    print(f"Task: {args.task}")
    print(
        "Switch VS Code -> Edge -> VS Code and keep each window active for "
        f"at least {args.debounce:.1f}s."
    )
    print("Screenshots are held in memory only. Press Ctrl+C to stop.")
    print("\nMonitoring...\n")

    deadline = time.monotonic() + args.duration
    trigger_count = 0
    had_error = False
    try:
        while time.monotonic() < deadline:
            snapshot = monitor.poll_once()
            info = monitor.last_window
            app_name = info.app_name if info else "Unknown"
            title = info.window_title if info else "Unknown Window"
            screenshot_state = (
                f"captured ({len(snapshot.screenshot)} bytes)" if snapshot else "skipped"
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}]")
            print(f"APP: {app_name}")
            print(f"TITLE: {title}")
            print(f"EVENT: {monitor.last_event}")
            print(f"SCREENSHOT: {screenshot_state}")
            print("---")
            if snapshot:
                trigger_count += 1
            if info and info.error:
                print(f"metadata warning: {info.error}")
            if monitor.last_error:
                had_error = True
                print(f"monitor error: {monitor.last_error}")
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        pass

    print(f"\nStable events captured: {trigger_count}")
    if not had_error and trigger_count >= args.required_triggers:
        print("WINDOWS CONTEXT ACCEPTANCE TEST: PASS")
        return 0
    print("WINDOWS CONTEXT ACCEPTANCE TEST: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
