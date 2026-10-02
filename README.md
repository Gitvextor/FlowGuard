# FlowGuard

Windows task-detour and interruption-recovery assistant. This repository currently contains the platform-independent foundation delivered by Person A.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/foundation_demo.py
```

Configure an LLM only when a later classifier needs one. Copy `.env.example` to `.env`, then set either `OPENAI_API_KEY` or `GEMINI_API_KEY`.

## Contract

All later modules import models and protocols from `app.core`; they must not redefine their fields. Read `docs/ARCHITECTURE.md` and `docs/HANDOFF_01.md` before extending the project.
