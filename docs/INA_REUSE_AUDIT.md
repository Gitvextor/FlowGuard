# INA reuse audit

Source repository: [IntentAssistant/INA](https://github.com/IntentAssistant/INA), cloned locally as `../_upstream_INA` at `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`. INA is MIT-licensed.

| INA area | Decision | FlowGuard use |
|---|---|---|
| `utils/direct_llm_client.py` image resize, JPEG, base64, direct provider calls | Reuse with adaptation | Compact, attributed `app/ai/llm_client.py` |
| `config/api_config.py` provider defaults and environment keys | Reuse with adaptation | Stateless `APISettings`; FlowGuard does not write API keys |
| Intention + screen-context + LLM product flow | Reuse conceptually | Three-state FlowGuard pipeline |
| Prompt format | Reuse conceptually | C will create a new three-class JSON prompt |
| PyQt screen capture | Reuse conceptually | `mss` / Pillow Windows-safe primary-screen capture |
| `utils/activity.py`, Quartz, AppleScript, browser URL extraction | Do not reuse | B writes Windows foreground-window collection |
| rumps, pyobjc, py2app, DMG/signing scripts | Do not reuse | macOS-only |
| Dashboard, feedback learning, reflection and screenshot logging | Do not reuse | Outside holiday scope; screenshots must stay in memory |

Attribution is in `THIRD_PARTY_NOTICES.md`; no INA source is copied without its MIT notice being preserved.
