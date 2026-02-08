from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "keys.env"
load_dotenv(dotenv_path=str(ENV_PATH))


def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


_raw_flow = get_env("FLOW_CONFIG_PATH")
if _raw_flow:
    _flow_path = Path(_raw_flow)
    FLOW_CONFIG_PATH = _flow_path if _flow_path.is_absolute() else BASE_DIR / _flow_path
else:
    FLOW_CONFIG_PATH = BASE_DIR / "flows" / "competition_flow.yaml"

LOG_LEVEL = get_env("LOG_LEVEL", "WARN").upper()

