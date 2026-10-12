from PyQt6.QtWidgets import QListWidget


class TimelineWidget(QListWidget):
    def update_events(self, events):
        self.clear()
        for event in reversed(events[-10:]):
            state = event.state.value.replace("_", " ")
            self.addItem(f"{event.timestamp:%H:%M:%S}  {event.app_name}  ·  {state}\n{event.window_title}")
