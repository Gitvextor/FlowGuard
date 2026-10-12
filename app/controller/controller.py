"""D-stage orchestration of monitoring, classification, storage and recovery."""

from __future__ import annotations

import threading
from concurrent.futures import Future, ThreadPoolExecutor

from app.ai.classifier import ActivityClassifier
from app.ai.resume_anchor import ResumeAnchorGenerator, should_generate_resume_anchor
from app.context import ContextMonitor, EventDetector, WindowsContextProvider
from app.storage import SessionStore


class IntegratedController:
    """Keep model work off the UI thread and own the full session lifecycle."""

    def __init__(self, *, provider=None, classifier=None, store=None, resume_generator=None,
                 notifier=None, on_result=None, on_error=None, poll_interval_seconds=1.0,
                 debounce_seconds=1.5):
        self.provider = provider or WindowsContextProvider()
        self.classifier = classifier or ActivityClassifier()
        self.store = store or SessionStore()
        self.resume_generator = resume_generator or ResumeAnchorGenerator()
        self.notifier, self.on_result, self.on_error = notifier, on_result, on_error
        self.monitor = ContextMonitor(
            self.provider, EventDetector(debounce_seconds=debounce_seconds),
            poll_interval_seconds=poll_interval_seconds, on_snapshot=self._submit_snapshot,
            on_error=lambda exc: self._report_error(f"Context error: {exc}"))
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="FlowGuardAnalysis")
        self._lock, self._running, self._task, self._generation = threading.RLock(), False, "", 0
        self._futures: set[Future] = set()

    @property
    def running(self):
        with self._lock:
            return self._running

    def start(self, task):
        task = task.strip()
        if not task:
            raise ValueError("请输入当前任务。")
        with self._lock:
            if self._running:
                raise RuntimeError("FlowGuard 已在运行。")
            session_id = self.store.start_session(task)
            self._task, self._running = task, True
            self._generation += 1
        try:
            self.monitor.start(task)
        except Exception:
            with self._lock:
                self._running, self._task = False, ""
            self.store.end_session()
            raise
        return session_id

    def pause(self):
        with self._lock:
            if not self._running:
                return
            self._running = False
            self._generation += 1
        self.monitor.stop()
        try:
            self.store.end_session()
        except Exception as exc:
            self._report_error(f"Storage error: {exc}")
        with self._lock:
            self._task = ""

    def shutdown(self):
        self.pause()
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _submit_snapshot(self, snapshot):
        with self._lock:
            if not self._running:
                return
            generation = self._generation
        future = self._executor.submit(self._process_snapshot, snapshot, generation)
        with self._lock:
            self._futures.add(future)
        future.add_done_callback(self._future_done)

    def _process_snapshot(self, snapshot, generation):
        result = self.classifier.classify(snapshot)
        with self._lock:
            active, task = self._running and generation == self._generation, self._task
        if not active:
            return
        if result.confidence <= 0.0 or self.classifier.last_error:
            self._report_error("LLM request failed. Monitoring continues.")
            return
        event = self.classifier.to_history_event(snapshot, result)
        if event is None:
            return
        try:
            self.store.append_event(event)
            history = self.store.get_recent_events(10)
        except Exception as exc:
            self._report_error(f"Storage error: {exc}")
            return
        anchor = None
        if should_generate_resume_anchor(history, consecutive_distractions=2):
            anchor = self.resume_generator.generate(task, history[-5:])
        if result.state.value == "DISTRACTION" and self.notifier is not None:
            try:
                self.notifier.notify_distraction(task)
            except Exception as exc:
                self._report_error(f"Notification error: {exc}")
        if self.on_result:
            self.on_result(snapshot, result, history, anchor)

    def _future_done(self, future):
        with self._lock:
            self._futures.discard(future)
        try:
            future.result()
        except Exception as exc:
            self._report_error(f"Analysis error: {exc}")

    def _report_error(self, message):
        if self.on_error:
            try:
                self.on_error(message)
            except Exception:
                pass
