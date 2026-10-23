# Third-party notices

## Intent Assistant (INA)

The complete upstream [IntentAssistant/INA](https://github.com/IntentAssistant/INA) repository is included unchanged in `third_party/INA` at commit `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`. Its original MIT `LICENSE` is included there.

FlowGuard adapts the image resize/JPEG-compression/base64 and direct OpenAI/Gemini request structure from INA, notably `src/utils/direct_llm_client.py` and `src/config/api_config.py` at that commit. The adapted implementation is `app/ai/llm_client.py`.

For the Windows context milestone, FlowGuard also adapts the responsibilities and fail-safe sequencing of INA's `src/utils/activity.py` and `src/manager.py` at the same commit: foreground identity, exact-current-process identification, previous/current comparison, and metadata plus in-memory screenshot ordering. `app/context/` is a Windows rewrite using Win32 APIs, exact PID/HWND/title exclusion, App/title debounce, and FlowGuard's existing screenshot provider.

INA is licensed under the MIT License:

```text
Copyright (c) 2025 Intent Assistant Contributors
```

The INA MIT notice remains in `third_party/INA/LICENSE`. No INA macOS-specific Quartz/AppleScript, browser URL, UI, packaging, notification, feedback, or storage code is imported into the active Windows application; those files remain available in the upstream copy.

## Runtime libraries

The project uses Pillow, mss, requests, google-genai, PyQt6, pywin32, psutil, and python-dotenv. Their licenses remain with their respective authors; install them from the package indexes specified in `requirements.txt`.
