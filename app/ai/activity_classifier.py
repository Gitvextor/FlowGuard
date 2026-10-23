"""Three-state screenshot classifier built on FlowGuard's INA-derived client."""

from __future__ import annotations

import math

from app.core.models import ActivityState, ClassificationResult, ContextSnapshot

from .llm_client import LLMClient


class ClassificationUnavailableError(RuntimeError):
    """Raised when a screenshot cannot be classified reliably."""


class LLMActivityClassifier:
    """Classify task context using a vision model and explicit task intent."""

    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def classify(self, context: ContextSnapshot) -> ClassificationResult:
        prompt = self._build_prompt(context)
        response = self.client.analyze(
            context.screenshot,
            prompt,
            context={
                "task": context.task,
                "app_name": context.app_name,
                "window_title": context.window_title,
            },
        )
        if not isinstance(response, dict):
            raise ClassificationUnavailableError("模型客户端没有返回有效结果。")
        if "error" in response:
            raise ClassificationUnavailableError(str(response["error"]))

        data = response.get("data")
        if not isinstance(data, dict):
            raise ClassificationUnavailableError("模型没有返回结构化分类结果。")

        try:
            state = ActivityState(str(data["state"]).strip().upper())
            confidence_value = data["confidence"]
            if isinstance(confidence_value, bool):
                raise ValueError("confidence must be numeric")
            confidence = float(confidence_value)
            if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                raise ValueError("confidence must be between 0 and 1")
        except (KeyError, TypeError, ValueError) as exc:
            raise ClassificationUnavailableError(
                "模型返回的状态或置信度不符合约定。"
            ) from exc

        reason = str(data.get("reason", "")).strip()
        task_relation = str(data.get("task_relation", "")).strip()
        if not reason or not task_relation:
            raise ClassificationUnavailableError("模型结果缺少判断理由或任务关联。")

        return ClassificationResult(
            state=state,
            confidence=confidence,
            reason=reason,
            task_relation=task_relation,
        )

    @staticmethod
    def _build_prompt(context: ContextSnapshot) -> str:
        return f"""你是 FlowGuard 的任务上下文判断助手。请结合用户声明的任务、当前前台窗口和截图，判断这一刻的行为。

用户任务：<task>{context.task}</task>
前台应用：{context.app_name}
窗口标题：{context.window_title}

按以下规则判断：
1. MAIN_TASK：当前内容直接推进用户任务。
2. NECESSARY_DETOUR：搜索、阅读资料、沟通或其他临时操作有清楚的任务关联。
3. DISTRACTION：有明确证据表明当前行为与任务无关。
4. 不要只按应用类别判断；同一个浏览器或视频应用可能服务于不同任务。
5. 证据不足时降低 confidence，并优先避免把正常工作误判成偏航。
6. reason 说明截图或窗口中看到的依据；task_relation 用一句话说明它与用户任务的关系。
7. reason 和 task_relation 使用与用户任务相同的语言。

只返回一个 JSON 对象，字段必须是 state、confidence、reason、task_relation；state 只能取 MAIN_TASK、NECESSARY_DETOUR、DISTRACTION，confidence 为 0 到 1 的数字。不要使用 Markdown 代码块。"""
