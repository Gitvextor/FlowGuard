# FlowGuard Handoff 01

## Basic information

From: A

To: B

Date: 2026-10-02
Milestone: Foundation

## Completed

- A stable `ContextSnapshot`, `ClassificationResult`, `HistoryEvent`, `ResumeAnchor`, and `ActivityState` schema.
- `ContextProvider`, `ActivityClassifier`, and `ResumeAnchorGenerator` protocols.
- Cross-platform LLM client adapted from INA's MIT-licensed direct client.
- In-memory primary screenshot capture, local session storage, mock pipeline, and acceptance demo.

## Run

```powershell
cd flowguard
pip install -r requirements.txt
python scripts/foundation_demo.py
python -m unittest discover -s tests -v
```

Expected terminal line:

```text
FOUNDATION ACCEPTANCE TEST: PASS
```

## Public interfaces

```python
ContextProvider.capture(task) -> ContextSnapshot
ActivityClassifier.classify(context) -> ClassificationResult
ResumeAnchorGenerator.generate(task, history) -> ResumeAnchor
ScreenshotProvider.capture_primary_screen() -> bytes
LLMClient.analyze(image, prompt, context=None) -> dict
SessionStore.start_session(task)
SessionStore.append_event(event)
SessionStore.get_recent_events(n=5)
SessionStore.end_session()
FlowGuardController.start(task)
FlowGuardController.process_once()
FlowGuardController.stop()
```

## Files changed

- `app/core/`, `app/config/`, `app/ai/llm_client.py`, `app/storage/`, `app/capture/`, `app/controller/base_controller.py`
- `scripts/foundation_demo.py`, `tests/test_foundation.py`, project documentation

## Known issues

- Screenshot capture needs an interactive desktop and installed `mss`/Pillow.
- `LLMClient.test_api()` needs a user-supplied key; the acceptance demo validates its image pipeline without making a paid API request.
- B must implement Windows foreground-window metadata; A's mock context is intentional.

## Do not change

- Field names/types in `app/core/models.py`.
- Protocol signatures in `app/core/interfaces.py`.
- Screenshot non-persistence rule.
- `LLMClient.analyze(image, prompt, context=None)` signature.

## B P0

Create `app/context/windows_context.py`, `event_detector.py`, and `context_monitor.py`. Capture screenshots only after B's event detector confirms a stable context change. Use `ContextSnapshot` exactly as defined.

## Prompt for B / next Codex agent

```text
你正在继续 FlowGuard 项目，负责 B：Windows Context + Event Engine。

项目目录：flowguard/

先阅读：
1. README.md
2. docs/ARCHITECTURE.md
3. docs/HANDOFF_01.md
4. docs/INA_REUSE_AUDIT.md

先执行：
python scripts/foundation_demo.py
python -m unittest discover -s tests -v

只有出现 FOUNDATION ACCEPTANCE TEST: PASS 才开始。

仅完成 P0：
- 新建 app/context/windows_context.py、event_detector.py、context_monitor.py。
- 用 win32gui、win32process、psutil 读取前台窗口标题和进程名；异常、空标题、无窗口不得崩溃。
- WindowsContextProvider 必须实现 app.core.ContextProvider，返回既有 ContextSnapshot；不要改字段或重新定义模型。
- 轻量轮询 App/Title；只在稳定变化（建议 1.5 秒 debounce）后才截图，截图使用既有 ScreenshotProvider。
- 防止 FlowGuard 自己的窗口触发分析。
- 新增 tests/test_windows_context.py、tests/test_event_detector.py、scripts/context_demo.py、docs/HANDOFF_02.md。

不要做：UI、LLM Prompt、三分类、Resume Anchor、浏览器 URL、OCR、重构 A 的模块。

完成后必须运行 A 的验收和你的 Context Demo；更新 HANDOFF_02，写明公开接口、实测软件、已知问题、给 C 的 P0。
```
