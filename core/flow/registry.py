from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core.flow.state_node import StateNode


@dataclass
class FlowRegistry:
    nodes: dict[str, StateNode]
    start_state: str
    fallback_state: str

    @classmethod
    def from_yaml(cls, path: str | Path) -> "FlowRegistry":
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"flow config not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        start_state = config.get("start_state")
        fallback_state = config.get("fallback_state")
        states_cfg: dict[str, Any] = config.get("states", {})

        if not start_state or not fallback_state:
            raise ValueError("flow config must include start_state and fallback_state")
        if not states_cfg:
            raise ValueError("flow config has no states")

        nodes: dict[str, StateNode] = {}
        for state_name, state_info in states_cfg.items():
            node_path = state_info.get("node")
            if not node_path:
                raise ValueError(f"state '{state_name}' missing node path")
            node_cls = _load_class(node_path)
            if not issubclass(node_cls, StateNode):
                raise TypeError(f"node '{node_path}' is not a StateNode")
            nodes[state_name] = node_cls()

        if fallback_state not in nodes:
            raise ValueError(f"fallback_state '{fallback_state}' is not defined in states")

        return cls(nodes=nodes, start_state=start_state, fallback_state=fallback_state)

    def get_node(self, state_name: str) -> StateNode | None:
        return self.nodes.get(state_name) or self.nodes.get(self.fallback_state)


def _load_class(path: str) -> type[StateNode]:
    if ":" in path:
        module_path, class_name = path.split(":", 1)
    else:
        module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    node_cls = getattr(module, class_name, None)
    if node_cls is None:
        raise ImportError(f"cannot import '{class_name}' from '{module_path}'")
    return node_cls
