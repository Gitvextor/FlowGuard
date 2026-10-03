# FlowGuard Handoff 02

## Basic information

From: B

To: C

Date: 2026-10-03

Milestone: Windows Context + Event Engine

## Completed

- `WindowsContextProvider` reads foreground HWND, title, PID, and exact process name with `win32gui`, `win32process`, and `psutil`.
- Self-window exclusion uses the FlowGuard process ID, registered native HWNDs, or exact registered titles. Other `python.exe` processes remain valid user context.
- `EventDetector` compares normalized App/title pairs and emits only after a configurable stable period (default 1.5 seconds).
- `ContextMonitor` polls metadata without screenshots, captures only on a confirmed stable event, supports callbacks/background start-stop, and contains metadata/capture failures.
- Screenshots call A's `ScreenshotProvider.capture_primary_screen()` and remain in the shared `ContextSnapshot`; B adds no screenshot persistence.
- Empty titles, unavailable foreground windows, inaccessible processes, and Win32 errors are represented safely and do not terminate monitoring.

## Run

```powershell
python scripts/foundation_demo.py
python -m unittest discover -s tests -v
python scripts/context_demo.py
```

For a short smoke run:

```powershell
python scripts/context_demo.py --duration 5 --debounce 0.5
```

The interactive demo prints App, title, trigger state, and whether an in-memory screenshot was captured. For the intended acceptance path, keep VS Code, Edge, and VS Code active in sequence for at least the configured debounce duration.

## Validation record

Validated on the Windows development desktop on 2026-10-03:

- A's acceptance demo printed `FOUNDATION ACCEPTANCE TEST: PASS`.
- The full suite ran 17 tests successfully.
- A live four-second context smoke run read `wps.exe` and its window title, waited through the 0.5-second debounce, emitted exactly one stable event, and captured a 446,401-byte in-memory JPEG. Later unchanged polls took no additional screenshots.
- Automated detector tests cover the intended Code -> Edge -> Code sequence semantics, including transient switches and title-only changes. The presenter should still run the full interactive VS Code -> Edge -> VS Code path before recording the final demonstration because window availability is machine-dependent.

## Public interfaces

```python
WindowsContextProvider.capture(task) -> ContextSnapshot
WindowsContextProvider.get_foreground_window() -> ForegroundWindowInfo
WindowsContextProvider.register_own_window(hwnd, title=None)

EventDetector.observe(app_name, window_title, observed_at=None, excluded=False) -> bool
EventDetector.reset()

ContextMonitor.poll_once(task=None) -> ContextSnapshot | None
ContextMonitor.start(task)
ContextMonitor.stop(timeout=5.0)
```

`ContextMonitor.last_window`, `last_triggered`, and `last_error` are available for D's UI/status integration. D should register the real PyQt native HWND with `register_own_window()` once it exists; PID matching already excludes windows owned by the running FlowGuard process.

## Tests

- Foreground app/title/PID collection.
- Exact self-PID exclusion without globally excluding Python.
- Empty-window and Win32-error safety.
- Reuse of A's shared `ContextSnapshot` and screenshot provider.
- Initial stable event, transient switch suppression, App/title changes, self-window suppression, and normalization.
- Monitor captures exactly once after a stable event and never captures an excluded self-window.

## INA reuse and attribution

Reviewed public INA commit `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`:

- `src/utils/activity.py`: adapted the responsibility of identifying the foreground app/window and the exact-current-process idea. The implementation is a Windows rewrite and contains no `osascript`, Quartz, or browser URL collection.
- `src/manager.py::_detect_app_change()`: adapted previous/current comparison and fail-safe behavior, replacing App/domain checks with App/title debounce.
- `src/manager.py::_capture_screen_internal()`: retained the ordering principle of metadata plus an in-memory image, while calling FlowGuard's existing screenshot provider.

INA's MIT attribution remains in `THIRD_PARTY_NOTICES.md`; the audit is updated in `docs/INA_REUSE_AUDIT.md`.

## Known issues

- Windows secure desktops, lock screens, elevated windows, and some protected apps may return no HWND/title or deny process metadata. These observations are skipped rather than crashing.
- Some apps change their title frequently (for example, progress counters). Each title is intentionally a new context and must remain stable before capture.
- The holiday scope supports the primary screen only because A's screenshot provider is intentionally primary-screen-only.
- B does not read browser URLs, classify activity, create prompts, persist screenshots, or build UI/notifications.

## C P0

- Import `ContextSnapshot` and the other shared models from `app.core`; do not redefine fields.
- Implement the three-state classifier and strict JSON/error fallback for `MAIN_TASK`, `NECESSARY_DETOUR`, and `DISTRACTION`.
- Use B's emitted snapshots; do not add a second polling or screenshot loop.
- Generate truthful trajectory summaries and Resume Anchors from recorded evidence only.
- Keep API failures non-fatal and do not treat failures as high-confidence distraction.
