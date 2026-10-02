import io
import tempfile
import unittest
from datetime import datetime

from PIL import Image

from app.ai.llm_client import LLMClient
from app.config.api_config import APISettings, LLMProvider
from app.controller.base_controller import (
    FlowGuardController,
    MockClassifier,
    MockContextProvider,
    MockResumeGenerator,
)
from app.core.models import ActivityState, HistoryEvent
from app.storage.session_store import SessionStore


class FoundationTests(unittest.TestCase):
    def test_session_store_never_writes_screenshot(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SessionStore(directory)
            store.start_session("Write tests")
            store.append_event(
                HistoryEvent(datetime.now().astimezone(), "Code.exe", "test.py", ActivityState.MAIN_TASK, "Writing tests")
            )
            event = store.get_recent_events(1)[0]
            self.assertEqual(event.state, ActivityState.MAIN_TASK)
            self.assertFalse(any(path.suffix.lower() in {".jpg", ".jpeg", ".png"} for path in store.session_dir.iterdir()))

    def test_controller_follows_the_shared_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SessionStore(directory)
            controller = FlowGuardController(MockContextProvider(), MockClassifier(), store, MockResumeGenerator())
            controller.start("Finish a coding task")
            context, result, anchor = controller.process_once()
            self.assertEqual(context.task, "Finish a coding task")
            self.assertEqual(result.state, ActivityState.MAIN_TASK)
            self.assertTrue(anchor.next_step)
            controller.stop()

    def test_llm_image_preparation_is_in_memory(self):
        image = Image.new("RGB", (1600, 900), "navy")
        raw = io.BytesIO()
        image.save(raw, format="PNG")
        settings = APISettings(LLMProvider.OPENAI, "", "gpt-4o-mini", "https://api.openai.com/v1")
        compressed, encoded = LLMClient(settings).prepare_image_for_api(raw.getvalue())
        self.assertTrue(compressed.startswith(b"\xff\xd8"))
        self.assertTrue(encoded)


if __name__ == "__main__":
    unittest.main()
