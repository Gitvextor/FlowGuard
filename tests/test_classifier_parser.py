import json
import unittest

from app.ai.classifier_parser import ClassificationParseError, ClassificationParser
from app.core import ActivityState


class ClassificationParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ClassificationParser()
        self.valid = {
            "state": "NECESSARY_DETOUR",
            "confidence": 0.91,
            "reason": "The title names the current error reference.",
            "task_relation": "The title shows an error search relevant to the task.",
        }

    def test_parses_strict_json_text(self):
        result = self.parser.parse(json.dumps(self.valid))
        self.assertIs(result.state, ActivityState.NECESSARY_DETOUR)
        self.assertEqual(result.confidence, 0.91)

    def test_uses_raw_response_to_reject_leniently_parsed_non_json(self):
        response = {
            "data": self.valid,
            "raw_response": "Here is the answer: " + json.dumps(self.valid),
        }
        with self.assertRaises(ClassificationParseError):
            self.parser.parse(response)

    def test_clamps_confidence_to_zero_and_one(self):
        for confidence, expected in ((-0.2, 0.0), (1.4, 1.0)):
            with self.subTest(confidence=confidence):
                result = self.parser.parse({**self.valid, "confidence": confidence})
                self.assertEqual(result.confidence, expected)

    def test_rejects_missing_or_unexpected_fields(self):
        with self.assertRaisesRegex(ClassificationParseError, "missing fields"):
            self.parser.parse({key: value for key, value in self.valid.items() if key != "reason"})
        with self.assertRaisesRegex(ClassificationParseError, "unexpected fields"):
            self.parser.parse({**self.valid, "extra": "not allowed"})

    def test_rejects_invalid_state_and_non_numeric_confidence(self):
        with self.assertRaisesRegex(ClassificationParseError, "Unsupported state"):
            self.parser.parse({**self.valid, "state": "FOCUSED"})
        with self.assertRaisesRegex(ClassificationParseError, "confidence must be a number"):
            self.parser.parse({**self.valid, "confidence": "high"})

    def test_rejects_empty_non_json_and_api_error_responses(self):
        for response in ("", "classification: main task", {"error": "timeout"}):
            with self.subTest(response=response), self.assertRaises(ClassificationParseError):
                self.parser.parse(response)

    def test_rejects_markdown_fences_and_json_with_trailing_text(self):
        with self.assertRaises(ClassificationParseError):
            self.parser.parse("```json\n" + json.dumps(self.valid) + "\n```")
        with self.assertRaises(ClassificationParseError):
            self.parser.parse(json.dumps(self.valid) + "\nDone.")


if __name__ == "__main__":
    unittest.main()
