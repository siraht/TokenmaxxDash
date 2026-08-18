#!/usr/bin/env python3
"""Add publisher-owned benchmark datasets that do not affect plan normalization.

This stage runs after complete_data.py so benchmark publisher tables can be updated
without coupling their release cadence to provider-plan calculation logic.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data"
AS_OF = "2026-08-18"


def read(name: str) -> Any:
    return json.loads((DATA / name).read_text())


def write(name: str, value: Any) -> None:
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def upsert(rows: list[dict[str, Any]], row: dict[str, Any]) -> None:
    for index, existing in enumerate(rows):
        if existing["id"] == row["id"]:
            rows[index] = row
            return
    rows.append(row)


sources = read("sources.json")
benchmarks = read("benchmarks.json")
leaders = read("leaders.json")
summary = read("summary.json")

upsert(sources, {
    "id": "cursorbench-3-2",
    "title": "CursorBench 3.2 model-cost leaderboard",
    "publisher": "Cursor",
    "url": "https://cursor.com/en-US/cost-savings",
    "type": "external-benchmark",
    "supports": ["pass rate", "API-priced cost per task", "tokens per task", "agent steps per task"],
    "verifiedAt": AS_OF,
})

for suffix, model, score, cost, tokens, steps in [
    ("fable-5-max", "Fable 5 Max", 70.5, 17.32, 103525, 72),
    ("opus-5-max", "Opus 5 Max", 70.0, 8.23, 61838, 78),
    ("opus-5-extra-high", "Opus 5 Extra High", 69.3, 7.35, 54239, 72),
    ("fable-5-extra-high", "Fable 5 Extra High", 68.4, 11.73, 64971, 56),
    ("gpt-5-6-sol-max", "GPT-5.6 Sol Max", 67.2, 5.69, 28320, 48),
    ("opus-5-high", "Opus 5 High", 66.7, 3.91, 27932, 48),
    ("grok-4-5-high", "Grok 4.5 High", 66.7, 1.51, 19521, 33),
    ("fable-5-high", "Fable 5 High", 66.5, 8.77, 43747, 48),
    ("grok-4-5-medium", "Grok 4.5 Medium", 65.4, 1.54, 18914, 34),
    ("fable-5-medium", "Fable 5 Medium", 65.2, 6.80, 30366, 41),
    ("gpt-5-6-terra-max", "GPT-5.6 Terra Max", 64.9, 2.31, 32969, 47),
    ("gpt-5-6-sol-extra-high", "GPT-5.6 Sol Extra High", 64.5, 3.88, 19699, 38),
]:
    pass_rate = score / 100
    upsert(benchmarks, {
        "id": f"cursorbench-3-2-{suffix}",
        "kind": "coding-agent",
        "benchmark": "CursorBench",
        "version": "3.2",
        "agent": "Cursor Agent",
        "model": model,
        "score": score,
        "apiCostPerTaskUsd": cost,
        "apiUsdPerExpectedPass": round(cost / pass_rate, 6),
        "expectedPassesPerApiDollar": round(pass_rate / cost, 6),
        "tokensPerTask": tokens,
        "tokensPerExpectedPass": round(tokens / pass_rate, 2),
        "stepsPerTask": steps,
        "stepsPerExpectedPass": round(steps / pass_rate, 3),
        "sourceId": "cursorbench-3-2",
        "retrievedAt": AS_OF,
        "costMeaning": "Cursor-published average model API cost per CursorBench task; not subscription cost and not interchangeable with the Coding Agent Index.",
    })

benchmarks.sort(key=lambda row: (row.get("kind", ""), row.get("benchmark", ""), -(row.get("score") or 0), row["id"]))
sources.sort(key=lambda row: (row["publisher"].lower(), row["title"].lower()))
leaders["fableRelevantBenchmarkIds"] = [
    row["id"] for row in benchmarks if "fable" in (row.get("model", "") + row.get("id", "")).lower()
]
summary["externalBenchmarkRows"] = len(benchmarks)
summary["fableBenchmarkRowCount"] = len(leaders["fableRelevantBenchmarkIds"])

write("sources.json", sources)
write("benchmarks.json", benchmarks)
write("leaders.json", leaders)
write("summary.json", summary)
print(json.dumps({
    "externalBenchmarkRows": len(benchmarks),
    "cursorBenchRows": sum(row.get("benchmark") == "CursorBench" for row in benchmarks),
    "fableBenchmarkRows": summary["fableBenchmarkRowCount"],
}, indent=2))
