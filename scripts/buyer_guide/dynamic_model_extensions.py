"""Fast-moving model records added after the stable external benchmark catalog."""
from __future__ import annotations

from typing import Any


def apply_dynamic_model_extensions(models: dict[str, dict[str, Any]], top_catalog: list[str]) -> None:
    models["qwen3.6-35b"] = {
        "name": "Qwen3.6 35B A3B (Reasoning)",
        "provider": "Alibaba",
        "intelligence": 31.6,
        "input": 0.248,
        "cache": 0.059,
        "output": 1.485,
        "speed": 142.9,
        "source": "https://artificialanalysis.ai/models/qwen3-6-35b-a3b",
        "benchmarkConfidence": "direct-model",
        "benchmarkNote": "Artificial Analysis reasoning configuration; subscription and gateway routes should preserve the reasoning/non-reasoning distinction.",
    }
    if "qwen3.6-35b" not in top_catalog:
        top_catalog.append("qwen3.6-35b")
