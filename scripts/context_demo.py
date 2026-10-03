"""Interactive acceptance demo for FlowGuard's Windows context engine."""

import argparse
import sys
import time
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
        "--own-title",
        action="append",
        default=["FlowGuard"],
        help="Exact FlowGuard window title to exclude; may be repeated.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
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
    print("Screenshots are held in memory only. Press Ctrl+C to stop.\n")

    deadline = time.monotonic() + args.duration
    trigger_count = 0
    try:
        while time.monotonic() < deadline:
            snapshot = monitor.poll_once()
            info = monitor.last_window
            if info is None:
                print("app=Unknown | title= | trigger=NO | screenshot=NO")
            else:
                title = info.window_title or "<empty>"
                if len(title) > 90:
                    title = title[:87] + "..."
                if info.is_self:
                    state = "SKIP_SELF"
                elif not info.available:
                    state = "UNAVAILABLE"
                elif monitor.last_triggered:
                    state = "TRIGGER"
                else:
                    state = "WAIT"
                screenshot_state = (
                    f"YES ({len(snapshot.screenshot)} bytes)" if snapshot else "NO"
                )
                print(
                    f"app={info.app_name} | title={title} | "
                    f"trigger={state} | screenshot={screenshot_state}"
                )
                if snapshot:
                    trigger_count += 1
                if info.error:
                    print(f"  metadata warning: {info.error}")
            if monitor.last_error:
                print(f"  monitor error: {monitor.last_error}")
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        pass

    print(f"\nCONTEXT DEMO COMPLETE: {trigger_count} stable event(s) captured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
