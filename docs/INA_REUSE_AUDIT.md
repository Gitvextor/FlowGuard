# INA reuse audit

Source repository: [IntentAssistant/INA](https://github.com/IntentAssistant/INA), pinned at `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`. The complete upstream tree is preserved unchanged in `third_party/INA`; the working clone is `../_upstream_INA`. INA is MIT-licensed, and its original `LICENSE` is included in both copies.

| INA area | Decision | FlowGuard use |
|---|---|---|
| `src/utils/direct_llm_client.py` image resize, JPEG, base64, direct provider calls | Reuse with adaptation | Compact, attributed `app/ai/llm_client.py` |
| `config/api_config.py` provider defaults and environment keys | Reuse with adaptation | Stateless `APISettings`; FlowGuard does not write API keys |
| Intention + screen-context + LLM product flow | Reuse with adaptation | `app/ai/activity_classifier.py` combines user task, app/title, and screenshot |
| Prompt format | Reuse with adaptation | FlowGuard asks for three states and strict JSON; uncertainty is kept explicit |
| PyQt screen capture | Reuse conceptually | `mss` / Pillow Windows-safe primary-screen capture |
| `utils/activity.py` foreground-app responsibility and exact-current-process identification | Reuse with adaptation | B rewrites collection with Win32 APIs and uses exact PID/HWND/title self-window exclusion; no Quartz, AppleScript, or browser URL extraction |
| `manager.py` previous/current comparison and in-memory capture ordering | Reuse conceptually | B compares App/title with a 1.5-second debounce, then calls FlowGuard's existing `ScreenshotProvider` |
| Quartz, AppleScript, browser URL extraction | Do not reuse | macOS-only or outside the frozen scope |
| rumps, pyobjc, py2app, DMG/signing scripts | Do not reuse | macOS-only |
| Dashboard, feedback learning, reflection and screenshot logging | Preserved only in upstream copy | Outside current Windows scope; screenshots must stay in memory |

Attribution is in `THIRD_PARTY_NOTICES.md`. The upstream source copy is not modified; FlowGuard adaptations are kept in the active `app/` tree.
