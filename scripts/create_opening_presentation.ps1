$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$out = Join-Path $repo "output\presentation\FlowGuard_开题报告_最终版.pptx"
$uiImage = Join-Path $repo "tmp\presentation\flowguard_ui.png"
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = -1
$deck = $ppt.Presentations.Add()
$deck.PageSetup.SlideSize = 15

function T($slide,$text,$x,$y,$w,$h,$size,$color,$bold=$false) {
  $s=$slide.Shapes.AddTextbox(1,$x,$y,$w,$h); $s.TextFrame.TextRange.Text=$text
  $s.TextFrame.TextRange.Font.Name="Microsoft YaHei"; $s.TextFrame.TextRange.Font.NameFarEast="Microsoft YaHei"
  $s.TextFrame.TextRange.Font.Size=$size; $s.TextFrame.TextRange.Font.Color.RGB=$color
  $s.TextFrame.TextRange.Font.Bold=$(if($bold){-1}else{0}); $s.TextFrame.WordWrap=-1
  $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0; $s.TextFrame.MarginTop=0; $s.TextFrame.MarginBottom=0
  return $s
}
function S($title,$n) {
  $s=$deck.Slides.Add($deck.Slides.Count+1,12); $s.FollowMasterBackground=0; $s.Background.Fill.ForeColor.RGB=0x22170F
  T $s $title 56 32 830 52 27 0xFFFFFF $true | Out-Null
  T $s (("{0:D2}" -f $n)) 900 39 42 22 11 0xB8A999 $true | Out-Null
  return $s
}

$s=$deck.Slides.Add(1,12); $s.FollowMasterBackground=0; $s.Background.Fill.ForeColor.RGB=0x22170F
T $s "FlowGuard" 64 112 720 75 48 0xFFFFFF $true | Out-Null
T $s "智能任务护航与中断恢复助手" 66 202 760 55 27 0xF2C15B $true | Out-Null
T $s "A Context-Aware Task Detour and Interruption Recovery Assistant" 66 276 780 38 17 0xD9D1C7 | Out-Null
T $s "课程项目开题报告" 66 404 320 32 18 0xFFFFFF $true | Out-Null
T $s "Windows · Python · PyQt6 · 多模态三分类" 66 449 480 28 14 0x948879 | Out-Null

$s=S "研究背景：跨应用切换并不等于分心" 2
T $s "真实任务需要频繁跨应用" 58 112 420 42 24 0xF2C15B $true | Out-Null
T $s "编程需要查文档，论文写作需要找资料，小组作业需要即时沟通。传统屏蔽工具往往只看应用名称，容易把合理行为误判为分心。" 58 173 430 150 19 0xFFFFFF | Out-Null
T $s "核心矛盾" 565 112 240 42 24 0xF2C15B $true | Out-Null
T $s "同一个浏览器、聊天软件甚至视频网站，既可能服务于任务，也可能已经偏航。判断必须结合用户意图和当时上下文。" 565 173 330 150 19 0xFFFFFF | Out-Null
T $s "我们的切入点：识别必要绕路，并在真正偏航后帮助用户继续工作。" 58 412 835 55 20 0xFFFFFF $true | Out-Null

$s=S "相关工作：INA 提供了意图驱动的研究基础" 3
T $s "INA" 60 116 120 55 34 0xF2C15B $true | Out-Null
T $s "Intent Assistant 让用户声明意图，再结合屏幕上下文判断当前活动与意图的关系，并通过轻量提醒支持有意识的数字行为。" 60 186 390 155 18 0xFFFFFF | Out-Null
T $s "FlowGuard 的继承" 530 116 300 42 23 0xF2C15B $true | Out-Null
T $s "复用公开 INA 代码中的图像处理、模型请求和上下文判断思路，并保留 MIT 归属。" 530 172 345 105 18 0xFFFFFF | Out-Null
T $s "FlowGuard 的扩展" 530 326 300 42 23 0xF2C15B $true | Out-Null
T $s "面向 Windows，增加必要绕路类别、事件触发和 Resume Anchor。" 530 382 345 85 18 0xFFFFFF | Out-Null
T $s "INA 论文的 22 人实地研究结果属于原研究，不是 FlowGuard 的实验成绩。" 60 412 390 60 15 0xB8A999 | Out-Null

$s=S "研究问题围绕识别、恢复与调用效率" 4
T $s "RQ1" 60 122 90 42 24 0xF2C15B $true | Out-Null
T $s "如何识别必要绕路？" 150 122 330 42 22 0xFFFFFF $true | Out-Null
T $s "综合任务、App、标题和截图，避免把查资料、调试和协作直接判为分心。" 150 176 690 70 17 0xD9D1C7 | Out-Null
T $s "RQ2" 60 282 90 42 24 0xF2C15B $true | Out-Null
T $s "偏航后如何快速恢复？" 150 282 340 42 22 0xFFFFFF $true | Out-Null
T $s "从近期任务轨迹生成有证据的恢复提示，证据不足时明确说明未知。" 150 336 690 70 17 0xD9D1C7 | Out-Null
T $s "RQ3" 60 440 90 42 24 0xF2C15B $true | Out-Null
T $s "怎样减少无意义模型调用？" 150 440 390 42 22 0xFFFFFF $true | Out-Null
T $s "轻量轮询 App 和标题，变化稳定后才截图与分类。" 540 440 330 55 17 0xD9D1C7 | Out-Null

$s=S "目标是完成一条可运行、可演示、可评测的 Windows 闭环" 5
T $s "输入任务" 55 125 180 38 21 0xF2C15B $true | Out-Null
T $s "用户声明当前目标" 55 174 180 55 16 0xFFFFFF | Out-Null
T $s "理解上下文" 275 125 190 38 21 0xF2C15B $true | Out-Null
T $s "App、标题与主屏截图" 275 174 190 55 16 0xFFFFFF | Out-Null
T $s "三分类" 510 125 150 38 21 0xF2C15B $true | Out-Null
T $s "主任务、必要绕路、偏航" 510 174 190 55 16 0xFFFFFF | Out-Null
T $s "干预与恢复" 745 125 180 38 21 0xF2C15B $true | Out-Null
T $s "通知、历史与 Resume Anchor" 745 174 180 60 16 0xFFFFFF | Out-Null
T $s "冻结范围" 55 340 180 38 21 0xF2C15B $true | Out-Null
T $s "不做 URL 深读、OCR、RAG、Agent、自动控制电脑、多显示器适配和完整 INA 移植。" 245 336 650 95 18 0xFFFFFF | Out-Null

$s=S "三状态模型把合理支持活动单独识别" 6
T $s "MAIN TASK" 55 120 260 42 24 0x45D483 $true | Out-Null
T $s "直接推进当前任务\n例如在 VS Code 编辑调度代码" 55 175 260 95 17 0xFFFFFF | Out-Null
T $s "NECESSARY DETOUR" 355 120 290 42 24 0xF2C15B $true | Out-Null
T $s "直接、合理、短期地支持任务\n例如查当前错误或论文资料" 355 175 290 95 17 0xFFFFFF | Out-Null
T $s "DISTRACTION" 700 120 220 42 24 0xE45B5B $true | Out-Null
T $s "缺少合理任务关联\n例如无关娱乐或购物" 700 175 220 95 17 0xFFFFFF | Out-Null
T $s "微信和浏览器首页等证据不足场景仍输出三类之一，但降低置信度，不新增 UNCERTAIN。" 55 395 845 65 18 0xD9D1C7 $true | Out-Null

$s=S "系统采用事件触发的分层架构" 7
T $s "Windows Context" 55 120 210 38 21 0xF2C15B $true | Out-Null
T $s "轻量读取 App 和窗口标题\n约 1.5 秒稳定变化后截图" 55 170 220 100 16 0xFFFFFF | Out-Null
T $s "Activity Classifier" 300 120 230 38 21 0xF2C15B $true | Out-Null
T $s "多模态模型输出三状态、置信度、理由和任务关系" 300 170 225 100 16 0xFFFFFF | Out-Null
T $s "Session History" 555 120 210 38 21 0xF2C15B $true | Out-Null
T $s "仅保存事件摘要\n截图始终只在内存中" 555 170 210 100 16 0xFFFFFF | Out-Null
T $s "Intervention" 790 120 150 38 21 0xF2C15B $true | Out-Null
T $s "偏航通知与恢复提示" 790 170 150 80 16 0xFFFFFF | Out-Null
T $s "后台线程承担网络调用，UI 只接收结果信号；API 错误不会让程序退出。" 55 400 840 58 18 0xFFFFFF $true | Out-Null

$s=S "一次完整用户流程" 8
T $s "任务" 60 112 100 35 20 0xF2C15B $true | Out-Null
T $s "完成操作系统 Priority Scheduling 实验" 170 112 650 35 19 0xFFFFFF $true | Out-Null
T $s "VS Code" 60 205 170 35 21 0x45D483 $true | Out-Null
T $s "编辑调度函数\nMAIN TASK" 60 252 170 75 17 0xFFFFFF | Out-Null
T $s "Stack Overflow" 290 205 210 35 21 0xF2C15B $true | Out-Null
T $s "查询当前问题\nNECESSARY DETOUR" 290 252 210 75 17 0xFFFFFF | Out-Null
T $s "Bilibili" 560 205 160 35 21 0xE45B5B $true | Out-Null
T $s "无关娱乐\nDISTRACTION + 通知" 560 252 200 75 17 0xFFFFFF | Out-Null
T $s "返回工作" 790 205 150 35 21 0xFFFFFF $true | Out-Null
T $s "查看时间线与\nResume Anchor" 790 252 150 75 17 0xFFFFFF | Out-Null
T $s "系统只在真正偏航时干预，不替用户自动打开程序或操作电脑。" 60 430 820 45 18 0xD9D1C7 $true | Out-Null

$s=S "原型界面同时呈现状态、证据和恢复建议" 9
$s.Shapes.AddPicture($uiImage,0,-1,48,96,570,430) | Out-Null
T $s "任务与控制" 665 112 220 32 20 0xF2C15B $true | Out-Null
T $s "输入目标，开始或暂停监控。" 665 152 245 60 16 0xFFFFFF | Out-Null
T $s "状态与时间线" 665 248 220 32 20 0xF2C15B $true | Out-Null
T $s "展示分类、置信度、App、窗口标题和最近事件。" 665 288 245 75 16 0xFFFFFF | Out-Null
T $s "Resume Anchor" 665 400 220 32 20 0xF2C15B $true | Out-Null
T $s "只使用历史证据，未知问题明确写未知。" 665 440 245 65 16 0xFFFFFF | Out-Null

$s=S "评测重点是 NECESSARY DETOUR Recall" 10
T $s "数据集" 58 115 180 36 22 0xF2C15B $true | Out-Null
T $s "30–50 条人工标注场景\n覆盖编程、写作、学习、查资料、即时消息和娱乐\n三类尽量平衡" 58 165 360 150 17 0xFFFFFF | Out-Null
T $s "指标" 520 115 180 36 22 0xF2C15B $true | Out-Null
T $s "Accuracy\nMacro-F1\n各类 Precision / Recall / F1\n重点汇报必要绕路 Recall" 520 165 320 160 17 0xFFFFFF | Out-Null
T $s "规则基线" 58 385 180 36 22 0xF2C15B $true | Out-Null
T $s "离开主工作 App 就判为偏航。该基线能直接展示三分类对合理查资料行为的改进。" 240 382 630 75 18 0xFFFFFF | Out-Null

$s=S "四人采用接力开发，稳定接口减少合并风险" 11
T $s "A  基础架构" 55 115 220 36 21 0xF2C15B $true | Out-Null
T $s "统一模型与协议、LLM 客户端、截图、SessionStore、Mock 骨架" 55 162 350 85 16 0xFFFFFF | Out-Null
T $s "B  Windows 上下文" 505 115 260 36 21 0xF2C15B $true | Out-Null
T $s "前台窗口、标题、进程、稳定变化检测、自窗口排除" 505 162 350 85 16 0xFFFFFF | Out-Null
T $s "C  AI 逻辑" 55 310 220 36 21 0xF2C15B $true | Out-Null
T $s "三分类、结构化解析、失败回退、历史语义与 Resume Anchor" 55 357 350 85 16 0xFFFFFF | Out-Null
T $s "D  产品交付" 505 310 220 36 21 0xF2C15B $true | Out-Null
T $s "PyQt6 UI、后台线程、通知、评测、打包、演示与答辩材料" 505 357 350 85 16 0xFFFFFF | Out-Null

$s=S "七天里程碑先打通主线，再集中验证" 12
T $s "Day 1" 55 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Foundation" 55 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 2" 185 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Context" 185 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 3" 315 115 100 35 20 0xF2C15B $true | Out-Null; T $s "AI Engine" 315 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 4" 445 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Integration" 445 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 5" 575 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Bug Bash" 575 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 6" 705 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Evaluation" 705 157 130 30 16 0xFFFFFF | Out-Null
T $s "Day 7" 835 115 100 35 20 0xF2C15B $true | Out-Null; T $s "Packaging" 835 157 110 30 16 0xFFFFFF | Out-Null
T $s "每一棒先读取架构与上一份 HANDOFF，运行上一阶段验收，通过后再开发自己的 P0。" 55 300 850 55 19 0xFFFFFF $true | Out-Null
T $s "最后一天只允许打包、跨机测试、录制、PPT 优化和关键 Bug 修复，不再增加功能。" 55 402 850 55 18 0xD9D1C7 | Out-Null

$s=S "可行性来自明确边界、Mock 回退和分层测试" 13
T $s "技术可行" 55 118 200 36 22 0xF2C15B $true | Out-Null
T $s "Windows API、PyQt6、本地 JSON 和成熟视觉模型均有明确实现路径。" 55 168 360 90 17 0xFFFFFF | Out-Null
T $s "演示可行" 520 118 200 36 22 0xF2C15B $true | Out-Null
T $s "FLOWGUARD_MOCK=true 时不需要 API Key，也能演示完整三分类链路。" 520 168 340 90 17 0xFFFFFF | Out-Null
T $s "主要风险" 55 335 200 36 22 0xF2C15B $true | Out-Null
T $s "语义歧义、API 超时、窗口权限、通知不稳定、Resume Anchor 编造细节。" 55 385 360 80 17 0xFFFFFF | Out-Null
T $s "应对方式" 520 335 200 36 22 0xF2C15B $true | Out-Null
T $s "降低置信度、失败回退、异常隔离、通知冷却、只使用历史证据。" 520 385 340 80 17 0xFFFFFF | Out-Null

$s=S "预期成果是一套可复现的课程项目原型" 14
T $s "软件" 58 120 130 36 22 0xF2C15B $true | Out-Null
T $s "可运行的 Windows 图形界面与 onedir 包" 190 120 650 40 19 0xFFFFFF | Out-Null
T $s "工程" 58 205 130 36 22 0xF2C15B $true | Out-Null
T $s "稳定接口、测试、HANDOFF、固定 Demo 与错误回退" 190 205 650 40 19 0xFFFFFF | Out-Null
T $s "评测" 58 290 130 36 22 0xF2C15B $true | Out-Null
T $s "三分类指标、必要绕路 Recall、混淆情况与规则基线" 190 290 650 40 19 0xFFFFFF | Out-Null
T $s "结论" 58 405 130 36 22 0xF2C15B $true | Out-Null
T $s "FlowGuard 关注任务切换的原因，并在确认偏航后帮助用户从有依据的位置继续工作。" 190 400 680 75 20 0xFFFFFF $true | Out-Null

$s=S "参考资料" 15
T $s "INA 论文" 58 115 180 34 21 0xF2C15B $true | Out-Null
T $s "State Your Intention to Steer Your Attention: An AI Assistant for Intentional Digital Living\narXiv:2510.14513" 58 162 825 75 16 0xFFFFFF | Out-Null
T $s "开源实现" 58 275 180 34 21 0xF2C15B $true | Out-Null
T $s "IntentAssistant/INA，审计固定版本 db149cd98e817ad0b1bf6116ecd3b4406c35ecab，MIT License" 58 322 825 65 16 0xFFFFFF | Out-Null
T $s "项目规格" 58 425 180 34 21 0xF2C15B $true | Out-Null
T $s "FlowGuard 四人分工方案、最终项目 Brief、Architecture 与阶段 HANDOFF" 58 468 825 38 16 0xFFFFFF | Out-Null

$deck.SaveAs($out,24)
$deck.Close(); $ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)|Out-Null
Write-Output $out
