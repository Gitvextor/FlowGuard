$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$out = Join-Path $repo "output\presentation\FlowGuard_D_答辩汇报.pptx"
$pdf = Join-Path $repo "tmp\presentation\FlowGuard_D_答辩汇报.pdf"
$uiImage = Join-Path $repo "tmp\presentation\flowguard_ui.png"

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = -1
$deck = $ppt.Presentations.Add()
$deck.PageSetup.SlideSize = 15

function Add-Text($slide, $text, $x, $y, $w, $h, $size, $color, $bold=$false) {
    $shape = $slide.Shapes.AddTextbox(1, $x, $y, $w, $h)
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = "Microsoft YaHei"
    $shape.TextFrame.TextRange.Font.NameFarEast = "Microsoft YaHei"
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.Font.Bold = $(if ($bold) {-1} else {0})
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.MarginLeft = 0; $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0; $shape.TextFrame.MarginBottom = 0
    return $shape
}

function Add-Slide($title, $number) {
    $slide = $deck.Slides.Add($deck.Slides.Count + 1, 12)
    $slide.FollowMasterBackground = 0
    $slide.Background.Fill.ForeColor.RGB = 0x22170F
    Add-Text $slide $title 56 35 820 48 26 0xFFFFFF $true | Out-Null
    Add-Text $slide (("{0:D2}" -f $number)) 900 40 45 25 12 0xB8A999 $true | Out-Null
    return $slide
}

$slide = $deck.Slides.Add(1, 12)
$slide.FollowMasterBackground = 0; $slide.Background.Fill.ForeColor.RGB = 0x22170F
Add-Text $slide "FlowGuard" 66 120 750 80 48 0xFFFFFF $true | Out-Null
Add-Text $slide "Windows 任务绕路识别与中断恢复助手" 68 210 720 52 25 0xF2C15B $true | Out-Null
Add-Text $slide "D 阶段：UI、产品整合、评测与打包" 68 300 620 38 20 0xD9D1C7 | Out-Null
Add-Text $slide "课程项目答辩 · 2026" 68 465 360 28 14 0x948879 | Out-Null

$slide = Add-Slide "为什么需要 FlowGuard" 2
Add-Text $slide "跨应用工作本来就是任务的一部分" 58 108 500 48 25 0xF2C15B $true | Out-Null
Add-Text $slide "写代码时切到 Stack Overflow，可能是在解决当前错误。\n打开浏览器不等于分心。" 58 180 470 105 20 0xFFFFFF | Out-Null
Add-Text $slide "FlowGuard 综合任务、App、窗口标题与截图，区分：\n\nMAIN TASK    直接推进任务\nNECESSARY DETOUR    必要且短期的支持活动\nDISTRACTION    与任务缺少直接关系" 570 120 330 265 18 0xD9D1C7 | Out-Null
Add-Text $slide "核心改进：减少对【合理绕路】的误伤，并在真正偏航后提供恢复提示。" 58 425 840 50 18 0xFFFFFF $true | Out-Null

$slide = Add-Slide "D 阶段负责把模块变成可演示的软件" 3
Add-Text $slide "产品整合" 65 120 190 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "连接 ContextMonitor、分类器、SessionStore 与 Resume Anchor。" 65 170 360 80 17 0xFFFFFF | Out-Null
Add-Text $slide "用户体验" 500 120 190 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "任务输入、开始/暂停、实时状态、时间线、恢复提示。" 500 170 360 80 17 0xFFFFFF | Out-Null
Add-Text $slide "可靠性" 65 310 190 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "模型调用离开 UI 线程；失败结果不记录、不通知；退出时安全停止。" 65 360 360 90 17 0xFFFFFF | Out-Null
Add-Text $slide "交付" 500 310 190 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "36 条评测、规则基线、47 项测试、Windows onedir 包与固定演示流程。" 500 360 360 90 17 0xFFFFFF | Out-Null

$slide = Add-Slide "用户流程形成一条完整闭环" 4
Add-Text $slide "1  声明任务" 60 120 220 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "完成 Priority Scheduling 实验" 60 165 220 85 15 0xFFFFFF | Out-Null
Add-Text $slide "2  识别上下文" 370 120 220 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "VS Code → Stack Overflow → Bilibili" 370 165 220 65 16 0xFFFFFF | Out-Null
Add-Text $slide "3  适度干预" 680 120 220 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "仅 DISTRACTION 通知，60 秒冷却" 680 165 220 65 16 0xFFFFFF | Out-Null
Add-Text $slide "4  恢复工作" 215 330 220 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "依据最近历史生成 Resume Anchor" 215 375 220 65 16 0xFFFFFF | Out-Null
Add-Text $slide "5  本地留痕" 525 330 220 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "只保存事件摘要，截图始终停留在内存" 525 375 260 65 16 0xFFFFFF | Out-Null

$slide = Add-Slide "主界面让状态、证据与恢复建议同时可见" 5
$slide.Shapes.AddPicture($uiImage, 0, -1, 52, 95, 575, 430) | Out-Null
Add-Text $slide "任务控制" 670 118 210 30 20 0xF2C15B $true | Out-Null
Add-Text $slide "输入当前目标并开始或暂停护航。" 670 158 250 80 15 0xFFFFFF | Out-Null
Add-Text $slide "可解释状态" 670 255 210 30 20 0xF2C15B $true | Out-Null
Add-Text $slide "展示分类、置信度、App、窗口标题与最近事件。" 670 295 230 75 16 0xFFFFFF | Out-Null
Add-Text $slide "恢复提示" 670 405 210 30 20 0xF2C15B $true | Out-Null
Add-Text $slide "证据不足时明确写【不清楚】，不编造错误或行号。" 670 445 230 70 16 0xFFFFFF | Out-Null

$slide = Add-Slide "后台线程保证界面不会被模型请求卡住" 6
Add-Text $slide "ContextMonitor" 65 155 190 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "轻量轮询 App 与标题\n稳定变化后才截图" 65 210 200 90 16 0xFFFFFF | Out-Null
Add-Text $slide "单工作线程" 370 155 190 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "分类、存储和恢复生成\n全部离开 UI 主线程" 370 210 220 90 16 0xFFFFFF | Out-Null
Add-Text $slide "Qt 信号更新" 690 155 190 40 21 0xF2C15B $true | Out-Null
Add-Text $slide "只把结果送回界面\n暂停后丢弃迟到结果" 690 210 200 90 16 0xFFFFFF | Out-Null
Add-Text $slide "安全规则" 65 370 180 35 20 0xF2C15B $true | Out-Null
Add-Text $slide "confidence = 0 的失败分类跳过历史记录，也绝不会触发分心通知。" 250 368 640 70 18 0xFFFFFF | Out-Null

$slide = Add-Slide "评测重点检验必要绕路" 7
Add-Text $slide "36" 65 135 150 70 42 0xF2C15B $true | Out-Null
Add-Text $slide "人工标注场景\n三类各 12 条" 65 215 180 65 16 0xFFFFFF | Out-Null
Add-Text $slide "47 / 47" 315 135 210 70 42 0xF2C15B $true | Out-Null
Add-Text $slide "单元与集成测试通过" 315 215 210 45 16 0xFFFFFF | Out-Null
Add-Text $slide "0.000" 625 135 190 70 42 0xF2C15B $true | Out-Null
Add-Text $slide "规则基线的\nNECESSARY DETOUR Recall" 625 215 230 65 16 0xFFFFFF | Out-Null
Add-Text $slide "Mock 在固定场景集上 Accuracy 与 Macro-F1 均为 1.000。该结果只验证离线演示链路，不能代表真实模型准确率。" 65 355 820 85 18 0xFFFFFF | Out-Null

$slide = Add-Slide "当前版本已经达到可本机演示与打包的程度" 8
Add-Text $slide "已经实测" 60 115 230 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "Foundation Demo PASS\nContext 真实内存截图 PASS\nAI Mock Demo PASS\nUI 启动与退出 PASS\nWindows EXE 启动烟测 PASS" 60 170 350 230 17 0xFFFFFF | Out-Null
Add-Text $slide "尚需人工验收" 530 115 260 35 22 0xF2C15B $true | Out-Null
Add-Text $slide "另一台干净 Windows 电脑运行\n录制并回看 1–2 分钟备份视频\n确认 Git 分支后提交 c-stage" 530 170 360 180 17 0xFFFFFF | Out-Null
Add-Text $slide "当前不能声称跨机器兼容，也不能把 Mock 指标解释为真实模型效果。" 530 390 350 65 17 0xFFFFFF $true | Out-Null

$slide = Add-Slide "现场 Demo 使用固定的四步场景" 9
Add-Text $slide "VS Code" 65 120 180 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "编辑调度代码\nMAIN TASK" 65 170 180 80 17 0xFFFFFF | Out-Null
Add-Text $slide "Stack Overflow" 285 120 210 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "查询当前问题\nNECESSARY DETOUR" 285 170 210 80 17 0xFFFFFF | Out-Null
Add-Text $slide "Bilibili" 535 120 180 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "娱乐内容\nDISTRACTION + 通知" 535 170 215 95 15 0xFFFFFF | Out-Null
Add-Text $slide "返回工作" 765 120 150 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "查看时间线与\nResume Anchor" 765 170 160 80 17 0xFFFFFF | Out-Null
Add-Text $slide "演示前打开 Windows 通知权限，每个目标窗口稳定停留至少两秒。" 65 390 800 45 18 0xFFFFFF $true | Out-Null

$slide = Add-Slide "D 阶段完成了产品闭环，最终验收还差两项人工工作" 10
Add-Text $slide "代码闭环" 65 125 220 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "输入任务后，系统能捕获上下文、三分类、记录轨迹、通知偏航并提供恢复提示。" 65 175 360 115 18 0xFFFFFF | Out-Null
Add-Text $slide "交付闭环" 535 125 220 38 22 0xF2C15B $true | Out-Null
Add-Text $slide "测试、评测、Windows onedir 包、固定演示文档已经齐全。" 535 175 350 100 18 0xFFFFFF | Out-Null
Add-Text $slide "下一步：完成干净机器测试和备份视频，再宣布 FINAL ACCEPTANCE PASS。" 65 385 820 55 20 0xF2C15B $true | Out-Null

$deck.SaveAs($out, 24)
$deck.SaveAs($pdf, 32)
$deck.Close(); $ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($deck) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Output "PPTX=$out"
Write-Output "PDF=$pdf"
