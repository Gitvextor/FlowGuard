# FlowGuard Handoff Final

## 1. Basic information

From: D  
To: Project team  
Date: 2026-10-12  
Branch target: `c-stage` (the supplied workspace had no accessible `.git` metadata, so branch/commit identity must be confirmed before committing)

## 2. Current system status

Implemented: PyQt6 task/start/pause UI, current state and context, 10-entry timeline, Resume Anchor panel, event-triggered integration, one-worker background classification, safe session lifecycle, Qt tray notifications for `DISTRACTION` only, 60-second cooldown, 36-case evaluation, rule baseline, tests, and PyInstaller `onedir` packaging.

The controller consumes B's `ContextMonitor` snapshots and C's classifier/generator. It does not add polling, capture, URL, OCR, RAG, or computer automation. Confidence-zero failures are neither persisted nor notified. Screenshots are not written to history.

## 3. How to run

```powershell
pip install -r requirements.txt
$env:FLOWGUARD_MOCK="true"
python main.py
python -m unittest discover -s tests -v
python evaluation/run_eval.py
python -m PyInstaller --noconfirm packaging/FlowGuard.spec
```

The packaged app is `dist/FlowGuard/FlowGuard.exe` and must be distributed with the complete sibling `_internal` directory.

## 4. Files changed

- `app/ui/`: main window, timeline, and Resume Anchor widgets.
- `app/controller/controller.py`: monitor/classifier/storage/notification integration.
- `app/notifications/`: native Qt tray notification and cooldown.
- `evaluation/`: 36 manually labelled scenarios, metrics, baseline, and generated results.
- `tests/test_integration.py`: D-stage failure, pause, anchor, persistence, and cooldown coverage.
- `packaging/FlowGuard.spec`, `scripts/build_windows.ps1`, and `dist/FlowGuard/`.
- `main.py`, `requirements.txt`, this handoff, and the fixed demo script.

## 5. Public interfaces

```python
IntegratedController.start(task) -> session_id
IntegratedController.pause()
IntegratedController.shutdown()
NotificationCooldown.allow() -> bool
WindowsNotifier.notify_distraction(task) -> bool
```

All schemas and protocols continue to come from `app.core`.

## 6. Acceptance record

- Foundation demo: PASS.
- Unit/integration suite: 47 tests PASS on 2026-10-12.
- Windows context smoke demo: PASS with real in-memory screenshots. The automated terminal's animated title prevented a 0.5-second stable observation, so the real-path smoke used the demo's `--debounce 0`; detector tests still cover the production 1.5-second behavior.
- AI mock demo: PASS.
- UI offscreen construction/close smoke: PASS.
- Evaluation: PASS, 36 balanced samples.
- PyInstaller `onedir`: built successfully; packaged EXE stayed running during a five-second local smoke test.

## 7. Evaluation record

The checked-in result is an offline Mock evaluation, not paid-model accuracy and not a user study. On the deliberately reproducible 36-case set, Mock reported Accuracy 1.000 and Macro-F1 1.000; the leave-main-App baseline reported Accuracy 0.667, Macro-F1 0.556, and `NECESSARY_DETOUR` Recall 0.000. These numbers must not be generalized to real model quality.

## 8. Known issues and remaining human acceptance

- Clean-machine testing on a second Windows computer is not performed in this workspace. Blocking for final delivery: Yes.
- The 1–2 minute backup MP4 is not recorded. Blocking for presentation readiness: Yes.
- No real API key or paid model call was tested; this is explicitly not an acceptance prerequisite.
- Qt offscreen smoke reported a missing optional bundled font directory; the real packaged GUI launched successfully on the development machine.
- Protected/elevated windows and secure desktops may not expose metadata or screenshots.
- Repeated start after pause creates a new session rather than reopening the ended session.

## 9. Do not change

Do not redefine `app.core`, add a second context/screenshot loop, persist screenshots, notify on `MAIN_TASK`/`NECESSARY_DETOUR`, or add URL/OCR/RAG/automatic-computer behavior.

## 10. Final manual checklist

1. Confirm the repository is on `c-stage` before committing.
2. Copy the entire `dist/FlowGuard/` directory to a clean Windows PC and run the fixed demo.
3. Verify notifications are permitted and the app starts without Python or an IDE installed.
4. Record and watch the backup MP4, then document its final location.
5. Only after these steps report `FLOWGUARD FINAL ACCEPTANCE TEST: PASS`.
