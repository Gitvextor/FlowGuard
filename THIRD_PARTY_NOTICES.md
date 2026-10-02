# Third-party notices

## Intent Assistant (INA)

FlowGuard adapts the image resize/JPEG-compression/base64 and direct OpenAI/Gemini request structure from [IntentAssistant/INA](https://github.com/IntentAssistant/INA), notably `src/utils/direct_llm_client.py` and `src/config/api_config.py` at commit `db149cd98e817ad0b1bf6116ecd3b4406c35ecab` (inspected 2026-10-02). The adapted implementation is `app/ai/llm_client.py`.

INA is licensed under the MIT License:

```text
Copyright (c) 2025 Intent Assistant Contributors
```

The full MIT grant is compatible with and preserved by this project's `LICENSE`. No INA macOS-specific activity, UI, packaging, notification, feedback, or storage code is included.

## Runtime libraries

The project uses Pillow, mss, requests, google-genai, PyQt6, pywin32, psutil, and python-dotenv. Their licenses remain with their respective authors; install them from the package indexes specified in `requirements.txt`.
