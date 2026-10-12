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

Launch the PyQt6 dashboard. On Windows with `pywin32` and `psutil`, it uses B's
foreground-window monitor; other environments fall back to the foundation mock chain:

```powershell
python main.py --ui
```

The dashboard is intentionally thin: task input, start/pause, three-state status, recent timeline, and Resume Anchor. Later Windows Context and AI modules can be injected through the existing `FlowGuardController` contracts.

Configure an LLM only when a later classifier needs one. Copy `.env.example` to `.env`, then set either `OPENAI_API_KEY` or `GEMINI_API_KEY`.

For the opening-defense script and the market-gap framing, see [`docs/FLOWGUARD_开题答辩讲稿.md`](docs/FLOWGUARD_开题答辩讲稿.md).

## Contract

All later modules import models and protocols from `app.core`; they must not redefine their fields. Read `docs/ARCHITECTURE.md` and `docs/HANDOFF_01.md` before extending the project.
