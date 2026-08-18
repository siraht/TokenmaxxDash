#!/usr/bin/env python3
"""Validate the generated static site without external dependencies."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = ROOT / "src" / "data"


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"a", "link"} and values.get("href"):
            self.references.append(values["href"] or "")
        elif tag in {"script", "img", "source"} and values.get("src"):
            self.references.append(values["src"] or "")


def resolve_reference(page: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("mailto:", "tel:", "data:", "#")):
        return None
    clean = parsed.path
    if not clean:
        return None
    target = DIST / clean.lstrip("/") if clean.startswith("/") else page.parent / clean
    if clean.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve()


def main() -> int:
    if not DIST.exists():
        raise SystemExit("dist/ does not exist; build the site first")

    errors: list[str] = []
    pages = sorted(DIST.rglob("*.html"))
    for page in pages:
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            target = resolve_reference(page, reference)
            if target is None:
                continue
            try:
                target.relative_to(DIST.resolve())
            except ValueError:
                errors.append(f"{page.relative_to(DIST)}: reference escapes dist/: {reference}")
                continue
            if not target.exists():
                errors.append(f"{page.relative_to(DIST)}: missing {reference}")

    plans = json.loads((DATA / "plans.json").read_text(encoding="utf-8"))
    models = json.loads((DATA / "models.json").read_text(encoding="utf-8"))
    benchmarks = json.loads((DATA / "benchmarks.json").read_text(encoding="utf-8"))
    quality_routes = json.loads((DATA / "quality-routes.json").read_text(encoding="utf-8"))
    task_estimates = json.loads((DATA / "subscription-task-estimates.json").read_text(encoding="utf-8"))
    leaders = json.loads((DATA / "leaders.json").read_text(encoding="utf-8"))

    required_pages = ["index.html", "plans/index.html", "leaders/index.html", "models/index.html", "benchmarks/index.html", "methodology/index.html", "community/index.html", "sources/index.html"]
    for relative in required_pages:
        if not (DIST / relative).exists():
            errors.append(f"missing required page: {relative}")

    required_data = ["plans.json", "benchmarks.json", "models.json", "quality-routes.json", "subscription-task-estimates.json", "leaders.json", "sources.json", "summary.json", "methodology.json"]
    for name in required_data:
        if not (DIST / "data" / name).exists():
            errors.append(f"missing public data file: data/{name}")

    for plan in plans:
        detail = DIST / "plans" / plan["id"] / "index.html"
        if not detail.exists():
            errors.append(f"missing plan detail page: {plan['id']}")

    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    plan_ids = {plan["id"] for plan in plans}
    benchmark_ids = {row["id"] for row in benchmarks}
    route_ids = {row["id"] for row in quality_routes}
    model_ids = {row["id"] for row in models}
    for plan in plans:
        if plan.get("calculationStatus") == "opaque" or str(plan.get("valueDisplay", "")).lower() == "unresolved":
            errors.append(f"legacy unresolved plan state in static dataset: {plan['id']}")
        for model_id in plan.get("modelCoverageIds", []):
            if model_id not in model_ids:
                errors.append(f"plan {plan['id']}: missing model {model_id}")
    for key, id_set in (("codingAgentCostQualityPareto", benchmark_ids), ("codingAgentTimeQualityPareto", benchmark_ids), ("codingAgentTokenQualityPareto", benchmark_ids), ("modelPriceIntelligencePareto", benchmark_ids), ("modelSpeedIntelligencePareto", benchmark_ids), ("planModelValueIntelligencePareto", route_ids), ("planAccessPriceIntelligencePareto", route_ids)):
        for row_id in leaders.get(key, []):
            if row_id not in id_set:
                errors.append(f"leaders.{key}: missing {row_id}")
    if leaders.get("subscriptionTaskEstimateCount") != len(task_estimates):
        errors.append("leaders.subscriptionTaskEstimateCount mismatch")

    for key in ("topNormalizedValue", "topMeasuredFrontierSubsidy"):
        plan_id = summary[key]["planId"]
        if plan_id not in plan_ids:
            errors.append(f"summary.{key}.planId does not exist: {plan_id}")

    if errors:
        print(f"Static validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(pages)} HTML pages, {len(plans)} plan details, {len(models)} model routes, {len(quality_routes)} quality routes, {len(task_estimates)} task estimates, and all internal references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
