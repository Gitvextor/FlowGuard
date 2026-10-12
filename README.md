# FlowGuard

Windows task-detour and interruption-recovery assistant. This repository contains the integrated Windows D-stage application. Mock mode provides an end-to-end demo without an API key.

For the agreed project scope and a Feishu-ready overview, read [the final project brief](docs/FLOWGUARD_FINAL_BRIEF_FEISHU.md).

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/foundation_demo.py
```

## Run the desktop app

```powershell
$env:FLOWGUARD_MOCK="true"
python main.py
python evaluation/run_eval.py
```

Build the Windows `onedir` package with `python -m PyInstaller --noconfirm packaging/FlowGuard.spec`. Distribute the complete `dist/FlowGuard/` directory, not the executable alone. See `docs/DEMO_SCRIPT.md` and `docs/HANDOFF_FINAL.md` for the fixed demo and verified limitations.
Configure an LLM only when a later classifier needs one. Copy `.env.example` to `.env`, then set either `OPENAI_API_KEY` or `GEMINI_API_KEY`.

## Contract

All later modules import models and protocols from `app.core`; they must not redefine their fields. Read `docs/ARCHITECTURE.md` and `docs/HANDOFF_01.md` before extending the project.

