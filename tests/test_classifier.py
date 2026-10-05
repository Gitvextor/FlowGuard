import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from app.ai.classifier import ActivityClassifier
from app.core import ActivityState, ContextSnapshot


class FakeClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def analyze(self, image, prompt, context=None):
        self.calls.append((image, prompt, context))
        if self.error:
            raise self.error
        return self.response


def snapshot(app_name="Code.exe", window_title="main.py - FlowGuard"):
    return ContextSnapshot(
        timestamp=datetime(2026, 10, 5, tzinfo=timezone.utc),
        task="Complete Python assignment",
        app_name=app_name,
        window_title=window_title,
        screenshot=b"the real in-memory snapshot image",
    )


class ActivityClassifierTests(unittest.TestCase):
    def test_passes_the_existing_snapshot_image_and_metadata_to_llm_client(self):
        response = {
            "data": {
                "state": "MAIN_TASK",
                "confidence": 0.88,
                "reason": "The editor title shows the task file.",
                "task_relation": "Editing the declared assignment file.",
            },
            "raw_response": '{"state":"MAIN_TASK","confidence":0.88,"reason":"The editor title shows the task file.","task_relation":"Editing the declared assignment file."}',
        }
        client = FakeClient(response=response)
        classifier = ActivityClassifier(client=client, mock=False)
        result = classifier.classify(snapshot())
        self.assertIs(result.state, ActivityState.MAIN_TASK)
        image, prompt, metadata = client.calls[0]
        self.assertEqual(image, b"the real in-memory snapshot image")
        self.assertIn("not, by itself, a distraction", prompt)
        self.assertEqual(metadata["task"], "Complete Python assignment")
        self.assertEqual(metadata["window_title"], "main.py - FlowGuard")

    def test_api_exception_returns_low_confidence_non_distraction_fallback(self):
        classifier = ActivityClassifier(client=FakeClient(error=TimeoutError("network timeout")), mock=False)
        result = classifier.classify(snapshot("Bilibili", "Funny videos"))
        self.assertIs(result.state, ActivityState.MAIN_TASK)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.reason, "Classification unavailable")
        self.assertIn("timeout", classifier.last_error)

    def test_non_json_response_falls_back_without_crashing(self):
        classifier = ActivityClassifier(client=FakeClient(response={"data": {"text": "not json"}}), mock=False)
        result = classifier.classify(snapshot())
        self.assertEqual(result.confidence, 0.0)
        self.assertIsNot(result.state, ActivityState.DISTRACTION)

    def test_mock_mode_covers_a_25_case_development_scenario_set(self):
        cases_path = Path(__file__).parent / "data" / "ai_scenarios.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 20)
        self.assertLessEqual(len(cases), 30)
        self.assertEqual(len(cases), 25)
        classifier = ActivityClassifier(mock=True)
        for case in cases:
            with self.subTest(case=case["name"]):
                context = snapshot(case["app_name"], case["window_title"])
                result = classifier.classify(context)
                self.assertEqual(result.state.value, case["state"])
                if "confidence_max" in case:
                    self.assertLessEqual(result.confidence, case["confidence_max"])

    def test_flowguard_mock_environment_switch_enables_mock_without_api_calls(self):
        client = FakeClient(error=AssertionError("must not call the API"))
        with patch.dict("os.environ", {"FLOWGUARD_MOCK": "true"}):
            classifier = ActivityClassifier(client=client)
        result = classifier.classify(snapshot())
        self.assertIs(result.state, ActivityState.MAIN_TASK)
        self.assertEqual(client.calls, [])

    def test_rate_limit_server_error_and_empty_response_use_safe_fallback(self):
        responses = (
            {"error": "HTTP 429 rate limit"},
            {"error": "HTTP 500 server error"},
            {"data": {"text": ""}},
        )
        for response in responses:
            with self.subTest(response=response):
                classifier = ActivityClassifier(client=FakeClient(response=response), mock=False)
                result = classifier.classify(snapshot())
                self.assertIs(result.state, ActivityState.MAIN_TASK)
                self.assertEqual(result.confidence, 0.0)
                self.assertIsNot(result.state, ActivityState.DISTRACTION)

    def test_history_event_is_extractively_built_and_failed_classification_is_skipped(self):
        context = snapshot("Microsoft Edge", "Priority Scheduling - Stack Overflow")
        result = ActivityClassifier(mock=True).classify(context)
        event = ActivityClassifier.to_history_event(context, result)
        self.assertEqual(event.app_name, context.app_name)
        self.assertEqual(event.window_title, context.window_title)
        self.assertIn(context.window_title, event.summary)
        self.assertIn(result.state.value, event.summary)

        failed = ActivityClassifier(client=FakeClient(error=TimeoutError()), mock=False)
        failed_result = failed.classify(context)
        self.assertIsNone(ActivityClassifier.to_history_event(context, failed_result))


if __name__ == "__main__":
    unittest.main()
