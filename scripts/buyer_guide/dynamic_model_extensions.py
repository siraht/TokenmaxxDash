"""Fast-moving and synthetic route records added after the stable model catalog."""
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

    # Kimi documents K3 256K and K3 1M as the same checkpoint and quality,
    # while the 1M route consumes approximately twice the plan quota. Keeping
    # them as separate routes lets the subscription adapter apply that weight.
    kimi = models.get("kimi-k3")
    if kimi:
        models["kimi-k3-256k"] = {
            **kimi,
            "name": "Kimi K3 256K",
            "source": "https://www.kimi.com/resources/kimi-code-introduction",
            "benchmarkConfidence": "same-checkpoint-derived",
            "benchmarkNote": "Same K3 checkpoint and coding ability as the externally benchmarked K3 route; fixed at 256K context and charged at half the K3 1M plan quota.",
        }

    # Mixed-route records intentionally have no borrowed intelligence score or
    # API price. They permit measured raw-token capacity to be compared without
    # pretending an unknown model mix has one model's quality.
    models["ollama-mixed-coding-route"] = {
        "name": "Ollama Cloud measured mixed coding route",
        "provider": "Ollama",
        "intelligence": None,
        "input": None,
        "cache": None,
        "output": None,
        "speed": None,
        "source": "https://ollama.com/pricing",
        "benchmarkConfidence": "mixed-route-unscored",
        "benchmarkNote": "Measured lower bound spans an unresolved model mix; no single-model quality score is transferred.",
    }
    models["antigravity-mixed-coding-route"] = {
        "name": "Google Antigravity measured mixed coding route",
        "provider": "Google",
        "intelligence": None,
        "input": None,
        "cache": None,
        "output": None,
        "speed": None,
        "source": "https://antigravity.google/docs/plans",
        "benchmarkConfidence": "mixed-route-unscored",
        "benchmarkNote": "Compute-based Antigravity capacity spans Gemini and third-party models; no single-model quality score is transferred.",
    }

    for model_id in ("qwen3.6-35b", "kimi-k3-256k"):
        if model_id in models and model_id not in top_catalog:
            top_catalog.append(model_id)
