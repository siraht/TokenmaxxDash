"""Add current externally benchmarked model versions used by additional plans."""
from __future__ import annotations

from typing import Any


def apply_model_extensions(models: dict[str, dict[str, Any]], tasks: dict[str, dict[str, Any]],
                           top_catalog: list[str], open_catalog: list[str]) -> None:
    additions: dict[str, dict[str, Any]] = {
        "claude-opus-4.6": {
            "name": "Claude Opus 4.6", "provider": "Anthropic", "intelligence": 38.0,
            "input": 5.0, "cache": 0.50, "output": 25.0, "speed": 37.1,
            "source": "https://artificialanalysis.ai/models/claude-opus-4-6",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis non-reasoning high-effort result; the subscription selector does not expose this benchmark effort label.",
        },
        "claude-opus-4.7": {
            "name": "Claude Opus 4.7", "provider": "Anthropic", "intelligence": 54.0,
            "input": 5.0, "cache": 0.50, "output": 25.0, "speed": 51.4,
            "source": "https://artificialanalysis.ai/models/claude-opus-4-7",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis adaptive-max result; actual product effort can differ.",
        },
        "claude-sonnet-4.6": {
            "name": "Claude Sonnet 4.6", "provider": "Anthropic", "intelligence": 47.0,
            "input": 3.0, "cache": 0.30, "output": 15.0, "speed": 58.0,
            "source": "https://artificialanalysis.ai/models/claude-sonnet-4-6-adaptive",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis adaptive-max result; actual product effort can differ.",
        },
        "gpt-5.3-codex": {
            "name": "GPT-5.3 Codex", "provider": "OpenAI", "intelligence": 46.0,
            "input": 1.75, "cache": 0.175, "output": 14.0, "speed": 125.8,
            "source": "https://artificialanalysis.ai/models/gpt-5-3-codex",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis xhigh result; model is retained because current Zencoder documentation still lists it.",
        },
        "gpt-5.4": {
            "name": "GPT-5.4", "provider": "OpenAI", "intelligence": 53.0,
            "input": 2.50, "cache": 0.25, "output": 15.0, "speed": 124.7,
            "source": "https://artificialanalysis.ai/models/gpt-5-4",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis xhigh result; deprecated by its provider but still listed in Zencoder's selector.",
        },
        "gpt-5.4-mini": {
            "name": "GPT-5.4 mini", "provider": "OpenAI", "intelligence": 41.0,
            "input": 0.75, "cache": 0.075, "output": 4.50, "speed": 172.3,
            "source": "https://artificialanalysis.ai/models/gpt-5-4-mini",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis xhigh result; deprecated by its provider but still listed in Zencoder's selector.",
        },
        "gpt-5.5": {
            "name": "GPT-5.5", "provider": "OpenAI", "intelligence": 55.0,
            "input": 5.0, "cache": 0.50, "output": 30.0, "speed": 76.2,
            "source": "https://artificialanalysis.ai/models/gpt-5-5",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis xhigh result; deprecated by its provider but still listed in Zencoder's selector.",
        },
        "gemini-3.1-pro": {
            "name": "Gemini 3.1 Pro", "provider": "Google", "intelligence": 46.0,
            "input": 2.0, "cache": 0.20, "output": 12.0, "speed": 131.0,
            "source": "https://artificialanalysis.ai/models/gemini-3-1-pro",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis reasoning-high result; actual product effort can differ.",
        },
        "gemini-3-flash": {
            "name": "Gemini Flash 3.0", "provider": "Google", "intelligence": 38.0,
            "input": 0.50, "cache": 0.05, "output": 3.0, "speed": 175.0,
            "source": "https://artificialanalysis.ai/models/gemini-3-flash-reasoning",
            "benchmarkConfidence": "effort-specific",
            "benchmarkNote": "Artificial Analysis reasoning result; Zencoder's selector does not state reasoning effort.",
        },
        "grok-code-fast-1": {
            "name": "Grok Code Fast 1", "provider": "xAI", "intelligence": 22.0,
            "input": None, "cache": None, "output": None, "speed": None,
            "source": "https://artificialanalysis.ai/models/grok-code-fast-1",
            "benchmarkConfidence": "estimated",
            "benchmarkNote": "Artificial Analysis marks the score as estimated; no stable direct API token price is attached here.",
        },
    }
    for model_id, row in additions.items():
        models[model_id] = row
    for model_id in additions:
        if model_id not in top_catalog:
            top_catalog.append(model_id)
