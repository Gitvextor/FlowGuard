# FlowGuard

Windows task-detour and interruption-recovery assistant. FlowGuard does not replace a timer or blocker; it adds task-aware judgment for the moments when leaving the current app may be reasonable, then gives the user a concrete way to resume.

For the agreed project scope and a Feishu-ready overview, read [the final project brief](docs/FLOWGUARD_FINAL_BRIEF_FEISHU.md).

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/foundation_demo.py
```

Launch the PyQt6 dashboard. On Windows with `pywin32` and `psutil`, it uses the
foreground-window monitor. With a model API key, visual classification runs in a
background worker; without one, the UI labels its keyword rules as demo mode:

```powershell
python main.py --ui
```

The dashboard includes task input, start/pause, three-state status, recent timeline, and Resume Anchor. It discards late model results after a session is stopped, and reports model failures without writing them into the activity history.

To enable real classification, copy `.env.example` to `.env`, then set either `OPENAI_API_KEY` or `GEMINI_API_KEY`.

The complete upstream INA repository is preserved unchanged at [`third_party/INA`](third_party/INA) under its MIT license. FlowGuard adapts the task-aware judgment flow for Windows; macOS-specific code remains in the upstream copy.

For the opening-defense script and the market-gap framing, see [`docs/FLOWGUARD_开题答辩讲稿.md`](docs/FLOWGUARD_开题答辩讲稿.md).

## Contract

All later modules import models and protocols from `app.core`; they must not redefine their fields. Read `docs/ARCHITECTURE.md` and `docs/HANDOFF_01.md` before extending the project.
