# FlowGuard｜选题与国庆版本最终方案

> 文档版本：2026-10-03 定稿版
>
> 用途：飞书项目主页、开题介绍、组员与 AI 协作时的统一项目背景
>
> 版本原则：以本文件和各阶段 `HANDOFF` 为准；早期 V1/V2/V3 草案与聊天建议不再作为开发需求。

## 1. 一页摘要

**项目名称：**FlowGuard——智能任务护航与中断恢复助手

**英文副标题：**A Context-Aware Task Detour and Interruption Recovery Assistant

**一句话简介：**让 AI 理解用户为什么暂时离开任务，并在真正偏航后帮助用户从有依据的位置重新开始。

**给老师看的选题说明：**用户先声明当前任务。FlowGuard 在 Windows 上结合前台应用、窗口标题与必要时的屏幕截图，判断当前活动属于“主任务、必要绕路、真正偏航”哪一种。它允许查资料、调试等服务于任务的合理离开，只在确认偏航时提醒；同时依据近期任务轨迹生成 Resume Anchor，提示之前做到哪里、已知的待解决问题和可执行的下一步。系统采用事件触发分析，减少重复截图和模型调用，并通过可复现的场景集评估三分类及必要绕路识别效果。

**国庆版本的唯一目标：**完成一条能在 Windows 上运行、演示和评估的“输入任务 → 获取上下文 → 三分类 → 记录轨迹 → 偏航提醒 → 恢复提示”闭环。**它不是 INA 的完整 Windows 移植。**

## 2. 研究背景与原工作

数字任务常常需要在多个应用之间切换。同一个 Edge、微信或视频网站页面，可以是学习资料，也可以是与任务无关的娱乐。仅按应用名封禁，容易把合理查资料误判为分心。

本项目受 INA（Intent Assistant）的论文《State Your Intention to Steer Your Attention: An AI Assistant for Intentional Digital Living》启发。该论文为 **CHI 2026 Full Paper**。INA 让用户声明意图，再结合屏幕上下文、应用信息等判断活动是否与意图一致，并以轻量提醒支持用户。论文报告了一项 22 人、三周的实地研究；这些结果属于 **INA 原研究**，不是 FlowGuard 的实验成绩。[论文](https://arxiv.org/abs/2510.14513)｜[项目主页](https://intentassistant.github.io/)｜[开源仓库](https://github.com/IntentAssistant/INA)

须区分两件事：**论文实验系统**描述了 Gemini 2.0 Flash 及云端后端；**当前公开 INA 仓库**提供 macOS 桌面程序及直接调用 OpenAI/Gemini 的代码。FlowGuard 复用的是公开代码中适合的实现与产品链路，不建设论文的云端研究基础设施。INA 仓库采用 MIT 许可，项目中保留了归属说明。[论文实现细节](https://arxiv.org/html/2510.14513)｜[INA README](https://github.com/IntentAssistant/INA)｜[INA LICENSE](https://github.com/IntentAssistant/INA/blob/main/LICENSE)

## 3. 我们的研究问题与相对 INA 的改进

**目标用户与场景：**需要频繁跨应用工作的 Windows 用户，优先考虑学生写代码、查资料、完成课程报告和论文写作。产品帮助用户判断“这次切换是否仍服务于当前目标”，而非给某个应用贴永久的好坏标签。

**问题 1：如何识别“必要绕路”？** 用户从 VS Code 切到 Stack Overflow 查当前报错，虽离开 IDE，却仍在推进任务。因此把 INA 偏重的任务相关/偏离判断细化为三种状态，重点检验必要绕路的识别能力。

**问题 2：偏航后如何继续？** 单次提醒只告诉用户“回来”，却没有恢复上下文。FlowGuard 将最近的任务轨迹压缩为 Resume Anchor，给出有证据的上次位置、当前问题和下一步；证据不足时明确说“不清楚”，不得编造代码行号或错误原因。

**问题 3：怎样减少无意义调用？** 对前台应用与窗口标题做轻量轮询，稳定变化后才截图和分类；相同上下文不重复调用。这里“降低调用成本”是设计目标，应在评测中用调用次数、延迟等数据验证，不能预先声称已实现某个百分比的节省。

这些是**相对于 INA 和本课程项目目标的设计增量**，不把它们表述为未经文献检验的绝对学术首创。

## 4. 唯一冻结版本：Windows 轻量闭环

| 功能 | 国庆版本要求 |
|---|---|
| 平台与界面 | Windows；Python + PyQt6；输入任务、开始/暂停、当前状态、近期时间线和恢复提示 |
| 上下文 | 前台 App、窗口标题、主屏幕截图；不读取浏览器 URL |
| 触发 | 约每秒轻量检查 App/标题；变化稳定约 1.5 秒后才截图并调用模型 |
| 理解 | 多模态 LLM 输出 `MAIN_TASK`、`NECESSARY_DETOUR` 或 `DISTRACTION`，含置信度及简短理由 |
| 历史与恢复 | 本地 JSON Session History；依据最近约 3–5 条事件生成 Resume Anchor |
| 干预 | 仅在真正偏航时发 Windows 通知；同类通知约 60 秒冷却；不自动操作电脑 |
| 交付 | 测试、评测脚本、Windows 可运行包、固定演示与备份视频 |

**三状态定义：**

- `MAIN_TASK`：当前活动直接推进用户声明的任务，如在 VS Code 编辑作业代码。
- `NECESSARY_DETOUR`：暂时离开主要工作界面，但与任务有直接、合理、短期的支持关系，如查当前报错的文档或论文资料。
- `DISTRACTION`：缺少合理任务关联，或原本的查资料已漂移到无关娱乐、购物等活动。

判断必须综合任务、App、标题和截图。微信、浏览器首页等证据不足的场景仍输出既有三类之一，但降低置信度；国庆版本**不新增 `UNCERTAIN` 类别**。

**明确不做：**登录与云端数据库、手机端、多设备同步、浏览器插件及 URL 深读、OCR 流水线、RAG/Agent、模型训练、长期个性化、完整 INA 反思学习、自动控制电脑、大规模用户研究、多显示器适配。旧稿中的 V1/V2/V3 分档、“不确定再调用第二模型”和“一键自动打开原程序”均不属于当前验收范围。

## 5. 一次完整的用户流程

1. 用户输入“完成操作系统 Priority Scheduling 实验”，点击“开始护航”。
2. VS Code 正在编辑相关文件，系统显示 `MAIN_TASK`，记录简短活动摘要。
3. 用户切到 Edge 查询 priority scheduling；窗口稳定变化后截一次主屏，系统显示 `NECESSARY_DETOUR`，不发提醒。
4. 用户打开 Bilibili 娱乐内容，系统判为 `DISTRACTION`，显示状态并发一次提醒；冷却期内不重复弹窗。
5. 用户返回工作时，界面展示从近期记录中生成的 Resume Anchor，例如“上次在 VS Code 编辑调度函数；具体未解决错误不明；下一步回到该文件继续验证”。用户可关闭提示。**只有历史明确显示某个错误或行号时，提示才可写出该细节。**

## 6. 系统流程与接口约定

```text
用户任务
  ↓
轻量读取前台 App / 窗口标题
  ↓ 变化稳定约 1.5 秒
截取主屏幕（仅在内存中）
  ↓
ContextSnapshot → ActivityClassifier → ClassificationResult
  ↓
SessionStore 保存 HistoryEvent → 时间线
  ↓ 确认偏航
Windows 通知 + ResumeAnchorGenerator → 恢复提示
```

**A 阶段已固定、后续不得重定义的公共模型：**

```python
ContextSnapshot(timestamp, task, app_name, window_title, screenshot)
ActivityState = MAIN_TASK | NECESSARY_DETOUR | DISTRACTION
ClassificationResult(state, confidence, reason, task_relation)
HistoryEvent(timestamp, app_name, window_title, state, summary)
ResumeAnchor(last_position, current_problem, next_step)
```

**公共接口：**`ContextProvider.capture(task)`、`ActivityClassifier.classify(context)`、`ResumeAnchorGenerator.generate(task, history)`、`LLMClient.analyze(image, prompt, context=None)`。B/C/D 应 import `app.core` 中的定义，不各自发明字段。截图不写入 Session Store；只保存任务、时间、App、标题、状态和简短摘要。

## 7. 技术路线与开源复用

**技术栈：**Windows、Python、PyQt6；`pywin32` + `psutil` 读前台窗口与进程；`mss`/Pillow 截图与压缩；OpenAI 或 Gemini 视觉 API；本地 JSON 存储；PyInstaller `onedir` 打包。模型和 API Key 通过配置选择，不在仓库提交密钥。

**明确的复用边界：**公开 INA 仓库固定审计版本为 `db149cd98e817ad0b1bf6116ecd3b4406c35ecab`。

| INA 公开源码 | FlowGuard 的用法 |
|---|---|
| `src/utils/direct_llm_client.py`、`src/config/api_config.py` | A 已改造图像缩放、JPEG、Base64、OpenAI/Gemini 请求及配置思路，形成统一 `LLMClient`；保留 MIT 归属 |
| `src/utils/activity.py` | B 参考前台应用识别职责与 `psutil` 自进程识别思路；`osascript`、Quartz 必须换成 Windows API |
| `src/manager.py` 中的变化检测与截图流程 | B 参考前后状态比较和内存截图时序；事件条件改为 App/标题变化，实际截图调用 A 的 `ScreenshotProvider` |
| INA 的提示词与“意图 + 屏幕上下文”方法 | C 参考判断思路，重新定义三分类 Prompt 与结构化输出 |
| macOS 菜单栏、通知、打包、浏览器 URL 和完整反馈反思系统 | 不直接移植 |

详见 [INA 复用审计](https://github.com/Gitvextor/FlowGuard/blob/main/docs/INA_REUSE_AUDIT.md) 与 [第三方声明](https://github.com/Gitvextor/FlowGuard/blob/main/THIRD_PARTY_NOTICES.md)。FlowGuard 仓库目前为私有仓库，组员需获得访问权限。

## 8. 四人接力与验收

| 负责人 | 职责 | 交付与验收 |
|---|---|---|
| A：基础架构 | INA 审计、统一模型/接口、LLM 客户端、截图、Session Store、Mock 控制链 | `python scripts/foundation_demo.py` 显示 `FOUNDATION ACCEPTANCE TEST: PASS`；交 `HANDOFF_01` |
| B：Windows 上下文 | 前台窗口/标题/进程、稳定变化检测、轻量监控、自窗口排除 | `context_demo.py` 展示 VS Code → Edge → VS Code，输出 App、标题、触发和截图状态；交 `HANDOFF_02` |
| C：AI 逻辑 | 三分类语义与 Prompt、JSON 解析和错误回退、轨迹摘要、可信 Resume Anchor、Mock 模式 | `ai_demo.py` 覆盖三类并生成 Anchor；交 `HANDOFF_03` |
| D：产品整合 | PyQt6 UI、后台线程、通知冷却、时间线、评测、打包和演示 | 真实链路、评测脚本、另一台 Windows 电脑安装运行、备份视频；交 `HANDOFF_FINAL` |

每棒先读 README、ARCHITECTURE 和上一份 HANDOFF，运行上一阶段验收；通过后才开发自己的 P0，补测试与已知问题，再交给下一棒。D 可并行准备开题 PPT 与界面草图，但不改写其他人的核心算法。

**原定七天里程碑：**10 月 1 日 A 基础；10 月 2 日 B Windows Context；10 月 3 日 C 三分类与恢复；10 月 4 日 D 功能整合；10 月 5 日全员边界情况测试；10 月 6 日评测；10 月 7 日打包、跨机验证、录演示和答辩排练。日期是计划，实际进度以仓库和 HANDOFF 验收为准。

## 9. 评估设计

- C 先准备 20–30 条开发用场景；D 扩为约 30–50 条人工标注的最终案例，覆盖编程、写作、学习、查资料、即时消息和娱乐，三类尽量平衡。
- 记录 Accuracy、Macro-F1、各类 Precision/Recall/F1，重点汇报 `NECESSARY_DETOUR` Recall；展示混淆矩阵和至少几条误判案例。
- 比较一个简单基线：离开主工作 App 就判为偏航。重点展示“写代码 → Stack Overflow 查当前错误”如何由 FlowGuard 识别为必要绕路。**基线是本项目构造的规则，不冒称 INA 原论文算法。**
- 如时间允许，记录每段演示的窗口变化次数、LLM 调用次数与响应时延，用实测数据说明事件触发的效果；不预设节省比例。
- 以上是课程项目的情景评测与工程验证，不能等同于 INA 的 22 人实地研究，也不能证明长期改善专注力。

## 10. 风险、隐私和回退

| 风险 | 第一版处理 |
|---|---|
| 微信、浏览器首页等语义歧义 | 结合任务、标题、截图；降低置信度，记录易错案例；不按 App 名一刀切 |
| Resume Anchor 编造细节 | 仅使用历史中已记录的证据；未知问题写“不清楚”，不推测代码行号 |
| API 超时、429、无效 JSON | 不让程序崩溃；状态栏显示分析不可用；不把失败结果当作高置信度偏航触发通知 |
| UI 被模型请求卡住 | 在后台线程执行请求，结果通过信号更新界面 |
| 频繁通知 | 只提醒 `DISTRACTION`，设置约 60 秒冷却 |
| 窗口权限与空标题 | 捕获异常、提供安全回退；保留可复现的已知问题 |
| 截图隐私 | 截图仅在内存中处理，不保存至会话目录；调用外部模型会向选定服务商发送截图，应在界面/说明中明确告知，允许暂停 |

## 11. 交付完成标准与演示脚本

**演示主线：**输入 Priority Scheduling 实验任务 → VS Code 显示 `MAIN_TASK` → Edge/Stack Overflow 查相关资料显示 `NECESSARY_DETOUR` → Bilibili 娱乐页显示 `DISTRACTION` 并弹一次通知 → 返回工作显示有依据的 Resume Anchor。

**完成标准：**Windows 可运行；开始/暂停正常；上下文变化触发稳定；三分类与历史正常；必要绕路不被无端提醒；偏航通知有冷却；恢复提示不编造；API 故障不致崩溃；UI 不被网络请求阻塞；评测脚本输出指标；另一台 Windows 电脑能运行打包结果；备份演示视频和答辩材料完成。全部通过后冻结国庆版本，不继续扩功能。

## 12. 当前工程进度（截至 2026-10-03）

整理时核对的 [FlowGuard 仓库 `main`](https://github.com/Gitvextor/FlowGuard) 代码基线为 `2bf3985`，已交付 **A Foundation**：统一模型与接口、INA LLM 能力适配、主屏截图、JSON 会话存储、Mock Controller、测试与 `HANDOFF_01`。A 的验收脚本此前输出 `FOUNDATION ACCEPTANCE TEST: PASS`，3 项单元测试通过；该验收只验证 LLM 客户端的图像处理，没有调用真实付费模型。该代码基线**尚未包含 B/C/D 的真实窗口监控、三分类、UI 或打包结果**；本文件描述的是最终目标，不能作为这些功能已完成的证据。后续以各阶段代码、测试和 HANDOFF 更新状态。

## 13. 给组员或其他 AI 的统一阅读顺序

1. 先读本文件，理解选题、唯一版本和验收目标。
2. 再读项目 `README.md`、`docs/ARCHITECTURE.md`、`docs/INA_REUSE_AUDIT.md`。
3. 进入开发时读上一棒的 `HANDOFF_XX.md`，先跑上一棒验收，按该交接的 P0 执行。
4. 若旧聊天建议与本文件冲突，以本文件的冻结范围和最新 HANDOFF 为准；不得擅自增加 URL 深读、OCR、RAG、Agent 或自动电脑控制。

## 参考资料

- INA 论文：[arXiv:2510.14513](https://arxiv.org/abs/2510.14513)；[HTML 全文](https://arxiv.org/html/2510.14513)。
- INA [项目主页](https://intentassistant.github.io/)与[MIT 开源仓库](https://github.com/IntentAssistant/INA)。
- FlowGuard [项目仓库](https://github.com/Gitvextor/FlowGuard)、[架构](https://github.com/Gitvextor/FlowGuard/blob/main/docs/ARCHITECTURE.md)、[A→B 交接](https://github.com/Gitvextor/FlowGuard/blob/main/docs/HANDOFF_01.md)。
- 整理依据：原《四人分工方案》、原《选 FlowGuard…》方案、群内初版介绍及 A 阶段实际代码与验收记录。
