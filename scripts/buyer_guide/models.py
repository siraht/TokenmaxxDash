"""Canonical model, external benchmark, and route-rate inputs."""
from __future__ import annotations

from typing import Any
AS_OF = "2026-08-18"
WEEKS_PER_MONTH = 365.2425 / 12 / 7
EUR_USD = 1.1572

# These are the two only workload presets exposed in the primary interface.
# 7:2:1 matches the external benchmark publisher's standardized token-price blend.
# Agentic-high-cache matches the public Codex telemetry used earlier in this project.
MIXES = {
    "standard": {"label": "Standardized 7:2:1", "fresh": 0.20, "cache": 0.70, "output": 0.10},
    "agentic": {"label": "Agentic high-cache", "fresh": 0.02594, "cache": 0.97108, "output": 0.00298},
}

MODELS: dict[str, dict[str, Any]] = {
    "claude-opus-4.8": {"name": "Claude Opus 4.8", "provider": "Anthropic", "intelligence": 56.0, "input": 5.0, "cache": 0.5, "output": 25.0, "speed": 54.2, "source": "https://artificialanalysis.ai/models/claude-opus-4-8", "status": "superseded"},
    "claude-opus-5": {"name": "Claude Opus 5", "provider": "Anthropic", "intelligence": 60.7, "input": 5.0, "cache": 0.5, "output": 25.0, "speed": 53.6, "source": "https://artificialanalysis.ai/models/claude-opus-5"},
    "claude-fable-5": {"name": "Claude Fable 5", "provider": "Anthropic", "intelligence": 59.9, "input": 10.0, "cache": 1.0, "output": 50.0, "speed": 62.6, "source": "https://artificialanalysis.ai/models/claude-fable-5"},
    "gpt-5.6-sol": {"name": "GPT-5.6 Sol", "provider": "OpenAI", "intelligence": 58.9, "input": 5.0, "cache": 0.5, "output": 30.0, "speed": 64.9, "source": "https://artificialanalysis.ai/models/gpt-5-6-sol"},
    "kimi-k3": {"name": "Kimi K3", "provider": "Moonshot AI", "intelligence": 57.1, "input": 3.0, "cache": 0.3, "output": 15.0, "speed": 35.4, "source": "https://artificialanalysis.ai/models/kimi-k3"},
    "gpt-5.6-terra": {"name": "GPT-5.6 Terra", "provider": "OpenAI", "intelligence": 55.0, "input": 2.0, "cache": 0.2, "output": 12.0, "speed": 131.8, "source": "https://artificialanalysis.ai/models/gpt-5-6-terra"},
    "grok-4.5": {"name": "Grok 4.5", "provider": "xAI", "intelligence": 53.8, "input": 2.0, "cache": 0.5, "output": 6.0, "speed": 62.3, "source": "https://artificialanalysis.ai/models/grok-4-5"},
    "claude-sonnet-5": {"name": "Claude Sonnet 5", "provider": "Anthropic", "intelligence": 53.4, "input": 2.0, "cache": 0.2, "output": 10.0, "speed": 74.7, "source": "https://artificialanalysis.ai/models/claude-sonnet-5", "note": "Promotional API prices through 2026-08-31; refresh after the scheduled price change."},
    "qwen3.8-max": {"name": "Qwen3.8 Max", "provider": "Alibaba", "intelligence": 53.4, "input": 2.0, "cache": 0.25, "output": 6.0, "speed": None, "source": "https://dataconomy.com/ai-models/qwen3-8-max/", "benchmarkConfidence": "secondary"},
    "gpt-5.6-luna": {"name": "GPT-5.6 Luna", "provider": "OpenAI", "intelligence": 51.2, "input": 0.2, "cache": 0.02, "output": 1.2, "speed": 174.9, "source": "https://artificialanalysis.ai/models/gpt-5-6-luna"},
    "glm-5.2": {"name": "GLM-5.2", "provider": "Z.AI", "intelligence": 51.1, "input": 1.4, "cache": 0.26, "output": 4.4, "speed": 112.7, "source": "https://artificialanalysis.ai/models/glm-5-2"},
    "muse-spark-1.1": {"name": "Muse Spark 1.1", "provider": "Meta", "intelligence": 50.6, "input": 1.25, "cache": 0.15, "output": 4.25, "speed": 130.0, "source": "https://artificialanalysis.ai/models/muse-spark-1-1"},
    "deepseek-v4-flash": {"name": "DeepSeek V4 Flash 0731", "provider": "DeepSeek", "intelligence": 50.0, "input": 0.14, "cache": 0.003, "output": 0.28, "speed": None, "source": "https://artificialanalysis.ai/models/deepseek-v4-flash", "routeNote": "Score assumes the current 0731 checkpoint; generic gateway aliases should be checked against their resolved route."},
    "qwen3.7-max": {"name": "Qwen3.7 Max", "provider": "Alibaba", "intelligence": 46.0, "input": 2.5, "cache": 0.25, "output": 7.5, "speed": 202.1, "source": "https://artificialanalysis.ai/models/qwen3-7-max"},
    "minimax-m3": {"name": "MiniMax M3", "provider": "MiniMax", "intelligence": 44.4, "input": 0.3, "cache": 0.06, "output": 1.2, "speed": 90.9, "source": "https://artificialanalysis.ai/models/minimax-m3"},
    "deepseek-v4-pro": {"name": "DeepSeek V4 Pro", "provider": "DeepSeek", "intelligence": 44.0, "input": 0.435, "cache": 0.004, "output": 0.87, "speed": 56.8, "source": "https://artificialanalysis.ai/models/deepseek-v4-pro"},
    "kimi-k2.6": {"name": "Kimi K2.6", "provider": "Moonshot AI", "intelligence": 44.0, "input": 0.95, "cache": 0.16, "output": 4.0, "speed": 40.2, "source": "https://artificialanalysis.ai/models/kimi-k2-6", "status": "superseded"},
    "mimo-v2.5-pro": {"name": "MiMo V2.5 Pro", "provider": "Xiaomi", "intelligence": 42.2, "input": 0.435, "cache": 0.0036, "output": 0.87, "speed": 39.2, "source": "https://artificialanalysis.ai/models/mimo-v2-5-pro"},
    "kimi-k2.7-code": {"name": "Kimi K2.7 Code", "provider": "Moonshot AI", "intelligence": 42.0, "input": 0.95, "cache": 0.19, "output": 4.0, "speed": 49.5, "source": "https://artificialanalysis.ai/models/kimi-k2-7-code"},
    "hy3": {"name": "Hy3", "provider": "Tencent", "intelligence": 41.0, "input": 0.136, "cache": 0.034, "output": 0.557, "speed": 70.8, "source": "https://artificialanalysis.ai/models/hy3"},
    "qwen3.6-plus": {"name": "Qwen3.6 Plus", "provider": "Alibaba", "intelligence": 39.6, "input": 0.5, "cache": 0.05, "output": 3.0, "speed": 53.6, "source": "https://artificialanalysis.ai/models/qwen3-6-plus"},
    "qwen3.7-plus": {"name": "Qwen3.7 Plus", "provider": "Alibaba", "intelligence": 39.0, "input": 0.4, "cache": 0.04, "output": 1.6, "speed": 52.8, "source": "https://artificialanalysis.ai/models/qwen3-7-plus"},
    "minimax-m2.7": {"name": "MiniMax M2.7", "provider": "MiniMax", "intelligence": 38.1, "input": 0.3, "cache": 0.06, "output": 1.2, "speed": 61.6, "source": "https://artificialanalysis.ai/models/minimax-m2-7", "status": "superseded"},
    "glm-5-turbo": {"name": "GLM-5 Turbo", "provider": "Z.AI", "intelligence": 38.1, "input": 1.2, "cache": 0.24, "output": 4.0, "speed": None, "source": "https://artificialanalysis.ai/models/glm-5-turbo", "status": "superseded"},
    "mimo-v2.5": {"name": "MiMo V2.5", "provider": "Xiaomi", "intelligence": 37.2, "input": 0.14, "cache": 0.0028, "output": 0.28, "speed": 91.0, "source": "https://artificialanalysis.ai/models/mimo-v2-5-0424"},
    "glm-4.7": {"name": "GLM-4.7", "provider": "Z.AI", "intelligence": 33.7, "input": 0.6, "cache": 0.11, "output": 2.2, "speed": 99.9, "source": "https://artificialanalysis.ai/models/glm-4-7", "status": "superseded"},
    "step-3.7-flash": {"name": "Step 3.7 Flash", "provider": "StepFun", "intelligence": 30.3, "input": 0.2, "cache": 0.04, "output": 1.15, "speed": 393.3, "source": "https://artificialanalysis.ai/models/step-3-7-flash"},
    "claude-haiku-4.5": {"name": "Claude Haiku 4.5", "provider": "Anthropic", "intelligence": 29.6, "input": 1.0, "cache": 0.1, "output": 5.0, "speed": 95.4, "source": "https://artificialanalysis.ai/models/claude-4-5-haiku-reasoning"},
    "gemma-4-31b": {"name": "Gemma 4 31B", "provider": "Google", "intelligence": 29.4, "input": None, "cache": None, "output": None, "speed": None, "source": "https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know"},
    "qwen3.5-omni-flash": {"name": "Qwen3.5 Omni Flash", "provider": "Alibaba", "intelligence": 19.0, "input": 0.1, "cache": 0.1, "output": 0.8, "speed": 238.6, "source": "https://artificialanalysis.ai/models/qwen3-5-omni-flash"},
    "muse-spark-1.2": {"name": "Muse Spark 1.2", "provider": "Meta", "intelligence": 43.0, "input": 1.25, "cache": 0.15, "output": 4.25, "speed": None, "source": "https://artificialanalysis.ai/models/muse-spark", "benchmarkConfidence": "version-match-medium", "benchmarkNote": "Artificial Analysis publishes the current Muse Spark family result; Command labels the route Muse Spark 1.2."},
    "muse-spark-1.2-contributor": {"name": "Muse Spark 1.2 Contributor", "provider": "Meta", "intelligence": 43.0, "input": 0.10, "cache": 0.002, "output": 0.20, "speed": None, "source": "https://artificialanalysis.ai/models/muse-spark", "benchmarkConfidence": "route-match-medium", "benchmarkNote": "Same advertised model family on a contributor-priced Command route."},
    "inkling": {"name": "Inkling", "provider": "Thinking Machines", "intelligence": 41.0, "input": 1.87, "cache": 0.374, "output": 4.68, "speed": 86.4, "source": "https://artificialanalysis.ai/models/inkling"},
    "inkling-small": {"name": "Inkling Small", "provider": "Thinking Machines", "intelligence": 40.0, "input": 0.30, "cache": 0.06, "output": 1.20, "speed": 101.5, "source": "https://artificialanalysis.ai/models/inkling-small"},
    "nemotron-3-ultra": {"name": "Nemotron 3 Ultra", "provider": "NVIDIA", "intelligence": 38.0, "input": 0.675, "cache": 0.25, "output": 2.675, "speed": 179.1, "source": "https://artificialanalysis.ai/models/nvidia-nemotron-3-ultra-550b-a55b"},
    "step-3.5-flash": {"name": "Step 3.5 Flash", "provider": "StepFun", "intelligence": 26.0, "input": 0.10, "cache": 0.02, "output": 0.30, "speed": 231.1, "source": "https://artificialanalysis.ai/models/step-3-5-flash", "status": "superseded"},
    "grok-4.6": {"name": "Grok 4.6", "provider": "xAI", "intelligence": None, "input": 2.0, "cache": 0.5, "output": 6.0, "speed": None, "source": "https://commandcode.ai/docs/plans/goat", "benchmarkNote": "No independent Artificial Analysis model score captured yet."},
    "gemini-3.7-flash": {"name": "Gemini 3.7 Flash", "provider": "Google", "intelligence": None, "input": 0.75, "cache": 0.075, "output": 3.75, "speed": None, "source": "https://commandcode.ai/docs/plans/goat", "benchmarkNote": "No exact independent Gemini 3.7 Flash score captured yet."},
    "qwen3.8-27b": {"name": "Qwen3.8 27B", "provider": "Alibaba", "intelligence": None, "input": 0.40, "cache": 0.04, "output": 3.0, "speed": None, "source": "https://commandcode.ai/docs/plans/goat", "benchmarkNote": "No exact independent score captured yet."},
    "kimi-k2.7-code-highspeed": {"name": "Kimi K2.7 Code HighSpeed", "provider": "Moonshot AI", "intelligence": 42.0, "input": 1.90, "cache": 0.38, "output": 8.0, "speed": None, "source": "https://artificialanalysis.ai/models/kimi-k2-7-code", "benchmarkConfidence": "same-weights-route", "benchmarkNote": "Uses the Kimi K2.7 Code model score; HighSpeed is a serving route."},
    "glm-5.2-fast": {"name": "GLM-5.2 Fast", "provider": "Z.AI", "intelligence": 51.1, "input": 3.0, "cache": 0.50, "output": 10.25, "speed": None, "source": "https://artificialanalysis.ai/models/glm-5-2", "benchmarkConfidence": "same-weights-route", "benchmarkNote": "Uses the GLM-5.2 model score; Fast is a serving route."},
    "glm-5.3": {"name": "GLM-5.3", "provider": "Z.AI", "intelligence": None, "input": None, "cache": None, "output": None, "speed": None, "source": "https://docs.z.ai/devpack/overview", "benchmarkNote": "New model; no independent Artificial Analysis score captured yet."},
    "composer-2.5": {"name": "Composer 2.5", "provider": "Cursor", "intelligence": None, "input": 0.5, "cache": 0.2, "output": 2.5, "speed": None, "source": "https://cursor.com/docs/models-and-pricing", "benchmarkNote": "Native Cursor agent benchmark exists; no directly comparable model Intelligence Index."},
}

# External coding-task rows. The primary task metric uses one benchmark family
# so pass rates and token counts remain comparable. Each result retains the
# publisher's harness; subscription $/success is a token-capacity counterfactual.
TASKS: dict[str, dict[str, Any]] = {
    # A single external coding-agent benchmark family is used for the primary
    # task metric so task scores remain comparable across models.  The published
    # raw tokens per task let us translate any subscription's effective $/M into
    # an estimated subscription $/successful task without pretending the plan's
    # harness is identical to the benchmark harness.
    "claude-opus-4.8": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Claude Code", "passRate": 0.61, "apiCost": 7.70, "tokensM": 17.9, "source": "https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-opencode"},
    "claude-opus-5": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Claude Code", "passRate": 0.67, "apiCost": 8.23, "tokensM": 21.8, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "claude-fable-5": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Claude Code", "passRate": 0.66, "apiCost": 11.70, "tokensM": 14.0, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "gpt-5.6-sol": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Codex", "passRate": 0.67, "apiCost": 7.08, "tokensM": 13.2, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "gpt-5.6-terra": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Codex", "passRate": 0.62, "apiCost": 2.21, "tokensM": 9.5, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "gpt-5.6-luna": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Codex", "passRate": 0.59, "apiCost": 0.31, "tokensM": 15.5, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "kimi-k3": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Kimi Code CLI", "passRate": 0.61, "apiCost": 3.18, "tokensM": 10.6, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "qwen3.8-max": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Claude Code", "passRate": 0.57, "apiCost": 3.86, "tokensM": 13.2, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "deepseek-v4-flash": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Codex", "passRate": 0.55, "apiCost": 0.07, "tokensM": 20.9, "source": "https://artificialanalysis.ai/agents/coding-agents"},
    "deepseek-v4-pro": {"benchmark": "AA Coding Agent Index v1.3", "harness": "Claude Code", "passRate": 0.31, "apiCost": 0.27, "tokensM": 9.8, "source": "https://artificialanalysis.ai/agents/coding-agents"},
}

TOP_CATALOG = [
    "claude-opus-5", "claude-fable-5", "gpt-5.6-sol", "kimi-k3", "gpt-5.6-terra",
    "grok-4.5", "claude-sonnet-5", "qwen3.8-max", "gpt-5.6-luna", "glm-5.2",
    "deepseek-v4-flash", "qwen3.7-max", "minimax-m3", "deepseek-v4-pro",
    "mimo-v2.5-pro", "kimi-k2.7-code", "hy3", "qwen3.7-plus", "mimo-v2.5",
    "muse-spark-1.2", "inkling", "inkling-small", "nemotron-3-ultra",
]
OPEN_CATALOG = [
    "kimi-k3", "glm-5.2", "deepseek-v4-flash", "qwen3.7-max", "minimax-m3",
    "deepseek-v4-pro", "mimo-v2.5-pro", "kimi-k2.7-code", "hy3", "qwen3.7-plus", "mimo-v2.5",
    "muse-spark-1.2", "inkling", "inkling-small", "nemotron-3-ultra",
]

# Provider-specific billing rates matter: a dollar-denominated pool only turns
# into token capacity after the route's actual billed input/cache/output rates.
OPEN_CODE_RATES = {
    "grok-4.5": {"fresh": 2.0, "cache": 0.30, "output": 6.0},
    "gpt-5.6-luna": {"fresh": 0.20, "cache": 0.02, "output": 1.20},
    "glm-5.3": {"fresh": 1.40, "cache": 0.26, "output": 4.40},
    "glm-5.2": {"fresh": 1.40, "cache": 0.26, "output": 4.40},
    "kimi-k3": {"fresh": 3.0, "cache": 0.30, "output": 15.0},
    "kimi-k2.7-code": {"fresh": 0.95, "cache": 0.19, "output": 4.0},
    "kimi-k2.6": {"fresh": 0.95, "cache": 0.16, "output": 4.0},
    "mimo-v2.5": {"fresh": 0.14, "cache": 0.0028, "output": 0.28},
    "mimo-v2.5-pro": {"fresh": 0.435, "cache": 0.003625, "output": 0.87},
    "minimax-m3": {"fresh": 0.30, "cache": 0.06, "output": 1.20},
    "minimax-m2.7": {"fresh": 0.30, "cache": 0.06, "output": 1.20},
    "qwen3.8-max": {"fresh": 2.0, "cache": 0.25, "output": 6.0},
    "qwen3.7-max": {"fresh": 2.50, "cache": 0.50, "output": 7.50},
    "qwen3.7-plus": {"fresh": 0.40, "cache": 0.04, "output": 1.60},
    "qwen3.6-plus": {"fresh": 0.50, "cache": 0.05, "output": 3.0},
    "deepseek-v4-pro": {"fresh": 0.435, "cache": 0.003625, "output": 0.87},
    "deepseek-v4-flash": {"fresh": 0.14, "cache": 0.0028, "output": 0.28},
    "hy3": {"fresh": 0.14, "cache": 0.035, "output": 0.58},
}
OPEN_CODE_USAGE = {
    "grok-4.5": 15, "gpt-5.6-luna": 15, "glm-5.3": 15, "glm-5.2": 60,
    "kimi-k3": 15, "kimi-k2.7-code": 60, "kimi-k2.6": 60,
    "mimo-v2.5": 60, "mimo-v2.5-pro": 15, "minimax-m3": 60,
    "qwen3.8-max": 15, "qwen3.7-max": 60, "qwen3.7-plus": 60,
    "qwen3.6-plus": 60, "deepseek-v4-pro": 15, "deepseek-v4-flash": 60,
    "hy3": 60,
}

# Command shows off-peak rates for 17 hours/day and peak rates for 7 hours/day.
# Use the time-weighted monthly average for a neutral all-day comparison.
DEEPSEEK_PRO_AVG = {"fresh": 0.8525, "cache": 0.0284166667, "output": 2.5575}
DEEPSEEK_FLASH_AVG = {"fresh": 0.2841666667, "cache": 0.0090416667, "output": 0.8525}
COMMAND_RATES = {
    **OPEN_CODE_RATES,
    "deepseek-v4-pro": DEEPSEEK_PRO_AVG,
    "deepseek-v4-flash": DEEPSEEK_FLASH_AVG,
    "grok-4.5": {"fresh": 2.0, "cache": 0.50, "output": 6.0},
    "grok-4.6": {"fresh": 2.0, "cache": 0.50, "output": 6.0},
    "gpt-5.6-sol": {"fresh": 5.0, "cache": 0.50, "output": 30.0},
    "gpt-5.6-terra": {"fresh": 2.0, "cache": 0.20, "output": 12.0},
    "gpt-5.6-luna": {"fresh": 0.20, "cache": 0.02, "output": 1.20},
    "qwen3.8-max": {"fresh": 2.0, "cache": 0.25, "output": 6.0},
    "qwen3.8-27b": {"fresh": 0.40, "cache": 0.04, "output": 3.0},
    "qwen3.7-max": {"fresh": 2.50, "cache": 0.50, "output": 7.50},
    "qwen3.7-plus": {"fresh": 0.40, "cache": 0.08, "output": 1.60},
    "qwen3.6-plus": {"fresh": 0.50, "cache": 0.10, "output": 3.0},
    "hy3": {"fresh": 0.14, "cache": 0.035, "output": 0.58},
    "minimax-m3": {"fresh": 0.30, "cache": 0.06, "output": 1.20},
    "muse-spark-1.2": {"fresh": 1.25, "cache": 0.15, "output": 4.25},
    "muse-spark-1.2-contributor": {"fresh": 0.10, "cache": 0.002, "output": 0.20},
    "kimi-k2.7-code-highspeed": {"fresh": 1.90, "cache": 0.38, "output": 8.0},
    "glm-5.2-fast": {"fresh": 3.0, "cache": 0.50, "output": 10.25},
    "gemini-3.7-flash": {"fresh": 0.75, "cache": 0.075, "output": 3.75},
    "inkling": {"fresh": 1.0, "cache": 0.17, "output": 4.05},
    "inkling-small": {"fresh": 0.50, "cache": 0.10, "output": 1.20},
    "step-3.7-flash": {"fresh": 0.20, "cache": 0.04, "output": 1.15},
    "step-3.5-flash": {"fresh": 0.10, "cache": 0.02, "output": 0.30},
    "nemotron-3-ultra": {"fresh": 0.60, "cache": 0.12, "output": 2.40},
    "claude-opus-5": {"fresh": 5.0, "cache": 0.50, "output": 25.0},
    "claude-opus-4.8": {"fresh": 5.0, "cache": 0.50, "output": 25.0},
    "claude-fable-5": {"fresh": 10.0, "cache": 1.0, "output": 50.0},
    "claude-sonnet-5": {"fresh": 2.0, "cache": 0.20, "output": 10.0},
    "claude-haiku-4.5": {"fresh": 1.0, "cache": 0.10, "output": 5.0},
}

COMMAND_GO_MODELS = [
    "gpt-5.6-luna", "grok-4.5", "kimi-k3", "kimi-k2.7-code",
    "kimi-k2.7-code-highspeed", "kimi-k2.6", "glm-5.3", "glm-5.2",
    "glm-5.2-fast", "deepseek-v4-flash", "deepseek-v4-pro", "mimo-v2.5",
    "mimo-v2.5-pro", "minimax-m3", "minimax-m2.7", "qwen3.8-max",
    "qwen3.8-27b", "qwen3.7-max", "qwen3.7-plus", "qwen3.6-plus", "hy3",
    "muse-spark-1.2-contributor", "inkling", "inkling-small", "step-3.7-flash",
    "step-3.5-flash", "nemotron-3-ultra",
]
COMMAND_GOAT_MODELS = list(dict.fromkeys(COMMAND_GO_MODELS + [
    "gpt-5.6-sol", "grok-4.6", "gemini-3.7-flash", "muse-spark-1.2",
]))
COMMAND_PRO_MODELS = list(dict.fromkeys(COMMAND_GOAT_MODELS + [
    "gpt-5.6-terra", "claude-sonnet-5", "claude-haiku-4.5",
]))
COMMAND_MAX_MODELS = list(dict.fromkeys(COMMAND_PRO_MODELS + [
    "claude-opus-5", "claude-opus-4.8", "claude-fable-5",
]))
