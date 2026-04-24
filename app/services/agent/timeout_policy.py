import os
import time


class StreamTimeoutPolicy:
    def __init__(self, idle_timeout_seconds: int | None = None):
        self.idle_timeout_seconds = idle_timeout_seconds or int(
            os.getenv("CHAT_STREAM_IDLE_TIMEOUT_SECONDS", "30")
        )

    def has_timed_out(self, last_event_at: float) -> bool:
        return time.monotonic() - last_event_at > self.idle_timeout_seconds
