"""Acceptance check for Person A's FlowGuard Foundation handoff."""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ai.llm_client import LLMClient
from app.capture.screenshot import ScreenshotProvider
from app.config.api_config import APISettings
from app.controller.base_controller import (
    FlowGuardController,
    MockClassifier,
    MockContextProvider,
    MockResumeGenerator,
)
from app.core.models import ActivityState, HistoryEvent
from app.storage.session_store import SessionStore


def _check(name: str, operation) -> object:
    try:
        result = operation()
        print(f"[{name}]\nPASS\n")
        return result
    except Exception as exc:
        print(f"[{name}]\nFAIL: {exc}\n")
        raise


def main() -> int:
    print("=== FlowGuard Foundation Demo ===\n")
    try:
        _check("CONFIG", APISettings.from_env)
        screenshot = _check("SCREENSHOT", ScreenshotProvider().capture_primary_screen)
        if not screenshot.startswith(b"\xff\xd8"):
            raise AssertionError("Screenshot provider did not return JPEG bytes.")

        def verify_llm_pipeline() -> None:
            compressed, encoded = LLMClient().prepare_image_for_api(screenshot)
            assert compressed.startswith(b"\xff\xd8") and encoded, "Image preparation failed."

        _check("LLM CLIENT", verify_llm_pipeline)

        with tempfile.TemporaryDirectory(prefix="flowguard_demo_") as directory:
            store = SessionStore(directory)

            def verify_storage() -> None:
                store.start_session("Finish FlowGuard foundation demo")
                store.append_event(
                    HistoryEvent(
                        timestamp=MockContextProvider().capture("demo").timestamp,
                        app_name="MockCode.exe",
                        window_title="demo.py",
                        state=ActivityState.MAIN_TASK,
                        summary="Storage smoke test.",
                    )
                )
                assert len(store.get_recent_events()) == 1

            _check("STORAGE", verify_storage)

            provider = MockContextProvider()
            _check("MOCK CONTEXT", lambda: provider.capture("Finish demo"))
            classifier = MockClassifier()
            _check("MOCK CLASSIFIER", lambda: classifier.classify(provider.capture("Finish demo")))

            controller_store = SessionStore(Path(directory) / "controller")
            controller = FlowGuardController(provider, classifier, controller_store, MockResumeGenerator())

            def verify_history() -> None:
                controller.start("Finish FlowGuard foundation demo")
                _, result, anchor = controller.process_once()
                assert result.state is ActivityState.MAIN_TASK
                assert anchor.next_step
                assert len(controller_store.get_recent_events()) == 1
                controller.stop()

            _check("HISTORY", verify_history)
            store.end_session()
    except Exception:
        print("FOUNDATION ACCEPTANCE TEST: FAIL")
        return 1

    print("FOUNDATION ACCEPTANCE TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
