from typing import Any
from unittest.mock import MagicMock

from meerqtt import MeerQTT


class TestClient:
    tested_instance: MeerQTT

    def __init__(self, meerqtt: MeerQTT):
        self.tested_instance = meerqtt

    def handle_submit(self, topic: str, message: Any):
        self.tested_instance.__handle_message(MagicMock, MagicMock, msg=message)
