"""JSON session storage. Screenshots are intentionally never persisted."""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import RLock

from app.core.models import ActivityState, HistoryEvent


class SessionStore:
    def __init__(self, root_dir: Path | str | None = None) -> None:
        self.root_dir = Path(root_dir or Path.home() / ".flowguard" / "sessions")
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._session_dir: Path | None = None
        self._task: str | None = None
        self._lock = RLock()

    @property
    def session_dir(self) -> Path | None:
        return self._session_dir

    def start_session(self, task: str) -> str:
        if not task.strip():
            raise ValueError("A non-empty task is required to start a session.")
        with self._lock:
            if self._session_dir is not None:
                raise RuntimeError("A session is already active.")
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self._session_dir = self.root_dir / session_id
            self._session_dir.mkdir(parents=True, exist_ok=False)
            self._task = task.strip()
            self._write_json(
                self._session_dir / "session.json",
                {
                    "session_id": session_id,
                    "task": self._task,
                    "started_at": datetime.now().astimezone().isoformat(),
                    "ended_at": None,
                    "status": "active",
                },
            )
            self._write_json(self._session_dir / "history.json", [])
            return session_id

    def append_event(self, event: HistoryEvent) -> None:
        with self._lock:
            history_path = self._require_active_session() / "history.json"
            history = self._read_json(history_path)
            history.append(
                {
                    **asdict(event),
                    "timestamp": event.timestamp.astimezone().isoformat(),
                    "state": event.state.value,
                }
            )
            self._write_json(history_path, history)

    def get_recent_events(self, n: int = 5) -> list[HistoryEvent]:
        if n < 1:
            return []
        with self._lock:
            if self._session_dir is None:
                return []
            records = self._read_json(self._session_dir / "history.json")[-n:]
        return [
            HistoryEvent(
                timestamp=datetime.fromisoformat(record["timestamp"]),
                app_name=record["app_name"],
                window_title=record["window_title"],
                state=ActivityState(record["state"]),
                summary=record["summary"],
            )
            for record in records
        ]

    def end_session(self) -> None:
        with self._lock:
            session_dir = self._require_active_session()
            session_path = session_dir / "session.json"
            session = self._read_json(session_path)
            session.update({"ended_at": datetime.now().astimezone().isoformat(), "status": "ended"})
            self._write_json(session_path, session)
            self._session_dir = None
            self._task = None

    def _require_active_session(self) -> Path:
        if self._session_dir is None:
            raise RuntimeError("No active session. Call start_session(task) first.")
        return self._session_dir

    @staticmethod
    def _read_json(path: Path):
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _write_json(path: Path, data: object) -> None:
        temporary = path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temporary.replace(path)
