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

## B reuse map: exact repositories and files

Public source: [IntentAssistant/INA](https://github.com/IntentAssistant/INA), pinned to commit `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`. This workstation has a copy at `../_upstream_INA`; on another machine, follow the pinned links or clone INA beside FlowGuard. Keep its MIT attribution if adapting code.

| Source | What B should take | Boundary |
|---|---|---|
| INA [`src/utils/activity.py`](https://github.com/IntentAssistant/INA/blob/db149cd98e817ad0b1bf6116ecd3b4406c35ecab/src/utils/activity.py), `get_current_app_name()` | Adapt its `psutil.Process(os.getpid())` / script-name fallback idea to identify FlowGuard's own process. Prefer FlowGuard's own HWND or exact window title for self-window exclusion. | Do not ignore every `python.exe`; the user may be working in Python. |
| INA `src/utils/activity.py`, `get_frontmost_app()` and `get_top_app_in_display()` | Reuse the *responsibility*: gather foreground app and window identity before analysis. | Their `osascript`/`Quartz` calls are macOS-only. Implement Windows collection with `win32gui.GetForegroundWindow`, `win32gui.GetWindowText`, `win32process.GetWindowThreadProcessId`, and `psutil.Process(pid).name()`. Do not copy the macOS calls. |
| INA [`src/manager.py`](https://github.com/IntentAssistant/INA/blob/db149cd98e817ad0b1bf6116ecd3b4406c35ecab/src/manager.py), `_detect_app_change()` | Adapt the previous/current state comparison and fail-safe error handling. | INA compares app/domain; FlowGuard compares app/window title. Add the planned 1.5-second debounce. Do not add browser URL reading. |
| INA `src/manager.py`, `_capture_screen_internal()` | Reuse the ordering and in-memory screenshot principle: collect metadata, capture image, pass bytes onward. | Call FlowGuard's existing `app.capture.ScreenshotProvider.capture_primary_screen()`; do not copy INA's display selection or screenshot cache. |

Already adapted in this repository: `app/ai/llm_client.py` from INA's `src/utils/direct_llm_client.py`. B should import existing `app.core` contracts and `app.capture.ScreenshotProvider`; B does not migrate the LLM client again. There is no other public application repository in B's scope. `pywin32` and `psutil` are dependencies for Windows integration, not upstream application code to paste wholesale.

## Prompt for B / next Codex agent

```text
你正在继续 FlowGuard 项目，负责 B：Windows Context + Event Engine。

项目目录：flowguard/

先阅读：
1. README.md
2. docs/ARCHITECTURE.md
3. docs/HANDOFF_01.md
4. docs/INA_REUSE_AUDIT.md

复用来源要明确：公开仓库 https://github.com/IntentAssistant/INA ，固定 commit db149cd98e817ad0b1bf6116ecd3b4406c35ecab；当前工作机有 ../_upstream_INA，若你的环境没有该副本，请按链接查看或另行 clone 到 FlowGuard 仓库外。
- 看 INA/src/utils/activity.py 的 get_current_app_name()：复用 psutil 获取自身进程及脚本名的思路，用于识别 FlowGuard 自身窗口；不能把所有 python.exe 一概忽略。
- 看 INA/src/utils/activity.py 的 get_frontmost_app()、get_top_app_in_display()：只复用“先取前台 App/窗口身份”的职责。osascript、Quartz 是 macOS 代码，Windows 必须改用 win32gui.GetForegroundWindow/GetWindowText、win32process.GetWindowThreadProcessId、psutil.Process(pid).name()。
- 看 INA/src/manager.py 的 _detect_app_change()：复用前后状态比较及错误保护的思路；把 INA 的 App/域名比较改成 FlowGuard 的 App/窗口标题比较，再做约 1.5 秒 debounce。不要读取浏览器 URL。
- 看 INA/src/manager.py 的 _capture_screen_internal()：复用“元数据 + 内存截图”的流程；实际截图直接调用本仓库 app.capture.ScreenshotProvider.capture_primary_screen()，不要复制 INA 的显示器选择、截图缓存代码。
- A 已把 INA/src/utils/direct_llm_client.py 的可跨平台部分适配到 app/ai/llm_client.py，B 不重复迁移。若改造 INA 代码，保留 MIT 归属并在 docs/INA_REUSE_AUDIT.md 记录。

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
