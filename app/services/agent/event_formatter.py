import json
from typing import Any


class ChatEventFormatter:
    def sse(self, payload: dict[str, Any]) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
