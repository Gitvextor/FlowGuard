"""Evidence-based Resume Anchor generation from the recorded session trail."""

from app.core.models import ActivityState, HistoryEvent, ResumeAnchor


class HistoryResumeAnchorGenerator:
    """Build a short recovery cue without inventing unrecorded task details."""

    def generate(self, task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        productive_events = [
            event
            for event in history
            if event.state in (ActivityState.MAIN_TASK, ActivityState.NECESSARY_DETOUR)
        ]
        if not productive_events:
            return ResumeAnchor(
                last_position="还没有可恢复的工作轨迹。",
                current_problem="当前记录里没有明确的问题线索。",
                next_step=f"回到任务“{task}”，从任务目标开始。",
            )

        last = productive_events[-1]
        location = " · ".join(part for part in (last.app_name, last.window_title) if part)
        summary = " ".join(last.summary.split())[:180]
        latest = history[-1]

        if latest.state is ActivityState.DISTRACTION:
            current_problem = "最近轨迹出现偏航；此前记录没有明确说明待解决的问题。"
            next_step = f"回到 {location}，从刚才的任务上下文继续。"
        elif last.state is ActivityState.NECESSARY_DETOUR:
            current_problem = summary or "刚才在查找与任务相关的信息。"
            next_step = f"带着刚才查到的信息，返回任务“{task}”。"
        else:
            current_problem = summary or "最近的轨迹没有记录明确的待解决问题。"
            next_step = f"回到 {location}，继续任务“{task}”。"

        return ResumeAnchor(
            last_position=location or "最近一次有效任务上下文",
            current_problem=current_problem,
            next_step=next_step,
        )
