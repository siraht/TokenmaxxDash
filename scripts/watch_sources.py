#!/usr/bin/env python3
"""Monitor provider, benchmark, measurement, and discovery pages for changes.

This script deliberately does not rewrite normalized plan values. It records fetch
metadata, raw and text hashes, and a candidate-change report for review. That
separation prevents dynamic page noise or a parser mistake from silently changing
public rankings.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "src" / "data" / "sources.json"
DEFAULT_STATE = ROOT / "research" / "source-state.json"
DEFAULT_CHANGES = ROOT / "research" / "changes" / "latest.json"
DEFAULT_SNAPSHOTS = ROOT / "research" / "snapshots"
USER_AGENT = (
    "TokenmaxxDashSourceMonitor/0.3 "
    "(+https://github.com/siraht/TokenmaxxDash; evidence-change detection)"
)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.suppressed = 0
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "template"}:
            self.suppressed += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "section", "article", "li", "tr", "br", "h1", "h2", "h3", "h4"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "template"} and self.suppressed:
            self.suppressed -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.suppressed:
            return
        self.parts.append(data)
        if self.in_title:
            self.title_parts.append(data)

    @property
    def text(self) -> str:
        return " ".join("".join(self.parts).split())

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def validate_sources(sources: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, source in enumerate(sources):
        prefix = f"source[{index}]"
        source_id = source.get("id")
        if not source_id:
            errors.append(f"{prefix}: missing id")
        elif source_id in seen:
            errors.append(f"{prefix}: duplicate id {source_id}")
        else:
            seen.add(source_id)
        url = source.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{prefix}: invalid URL {url!r}")
        if source.get("type") not in {"official", "measurement", "community-measurement", "external-benchmark", "secondary-benchmark", "external-methodology", "secondary"}:
            errors.append(f"{prefix}: unsupported type {source.get('type')!r}")
    return errors


def content_type(headers: Any) -> str:
    return str(headers.get("Content-Type", "")).split(";", 1)[0].strip().lower()


def decode_body(body: bytes, headers: Any) -> str:
    charset = None
    try:
        charset = headers.get_content_charset()
    except Exception:
        pass
    return body.decode(charset or "utf-8", errors="replace")


def normalized_document(body: bytes, media_type: str, headers: Any) -> tuple[str, str]:
    text = decode_body(body, headers)
    if media_type in {"application/json", "application/ld+json"} or text.lstrip().startswith(("{", "[")):
        try:
            parsed = json.loads(text)
            normalized = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            return normalized, ""
        except json.JSONDecodeError:
            pass
    if "html" in media_type or "<html" in text[:1000].lower():
        parser = VisibleTextParser()
        parser.feed(text)
        return parser.text, parser.title
    normalized = " ".join(text.split())
    return normalized, ""


def safe_suffix(media_type: str) -> str:
    if "json" in media_type:
        return "json"
    if "html" in media_type:
        return "html"
    if "xml" in media_type:
        return "xml"
    return "txt"


def fetch_source(
    source: dict[str, Any],
    previous: dict[str, Any] | None,
    timeout: float,
    snapshot_dir: Path,
    save_snapshots: bool,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    fetched_at = utc_now()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/json;q=0.9,text/plain;q=0.8,*/*;q=0.5",
        "Accept-Encoding": "identity",
    }
    if previous and previous.get("etag"):
        headers["If-None-Match"] = previous["etag"]
    if previous and previous.get("lastModified"):
        headers["If-Modified-Since"] = previous["lastModified"]

    request = Request(source["url"], headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            media_type = content_type(response.headers)
            normalized, title = normalized_document(body, media_type, response.headers)
            record = {
                "sourceId": source["id"],
                "sourceType": source["type"],
                "url": source["url"],
                "finalUrl": response.geturl(),
                "httpStatus": int(getattr(response, "status", 200)),
                "contentType": media_type,
                "contentLength": len(body),
                "rawSha256": sha256(body),
                "normalizedSha256": sha256(normalized.encode("utf-8")),
                "title": title or source.get("title", ""),
                "etag": response.headers.get("ETag"),
                "lastModified": response.headers.get("Last-Modified"),
                "fetchedAt": fetched_at,
                "error": None,
            }
            changed = previous is None or previous.get("normalizedSha256") != record["normalizedSha256"]
            change = None
            if changed:
                change = {
                    "sourceId": source["id"],
                    "sourceType": source["type"],
                    "url": source["url"],
                    "detectedAt": fetched_at,
                    "previousNormalizedSha256": previous.get("normalizedSha256") if previous else None,
                    "normalizedSha256": record["normalizedSha256"],
                    "previousTitle": previous.get("title") if previous else None,
                    "title": record["title"],
                    "status": "new-source" if previous is None else "content-changed",
                    "requiresReview": True,
                }
                if save_snapshots:
                    stamp = fetched_at.replace(":", "").replace("-", "")
                    destination = snapshot_dir / source["id"] / f"{stamp}.{safe_suffix(media_type)}.gz"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with gzip.open(destination, "wb") as handle:
                        handle.write(body)
                    change["snapshotPath"] = str(destination.relative_to(ROOT))
            return record, change
    except HTTPError as error:
        if error.code == 304 and previous:
            record = dict(previous)
            record["fetchedAt"] = fetched_at
            record["httpStatus"] = 304
            record["error"] = None
            return record, None
        return {
            "sourceId": source["id"],
            "sourceType": source["type"],
            "url": source["url"],
            "fetchedAt": fetched_at,
            "httpStatus": error.code,
            "error": f"HTTP {error.code}: {error.reason}",
            **({k: previous[k] for k in previous if k not in {"fetchedAt", "httpStatus", "error"}} if previous else {}),
        }, None
    except (URLError, TimeoutError, OSError) as error:
        return {
            "sourceId": source["id"],
            "sourceType": source["type"],
            "url": source["url"],
            "fetchedAt": fetched_at,
            "httpStatus": None,
            "error": str(error),
            **({k: previous[k] for k in previous if k not in {"fetchedAt", "httpStatus", "error"}} if previous else {}),
        }, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--changes", type=Path, default=DEFAULT_CHANGES)
    parser.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOTS)
    parser.add_argument("--source", action="append", dest="source_ids", help="Only monitor this source id; repeatable")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--only-on-change", action="store_true", help="With --write-state, leave tracked files untouched when no content changed")
    parser.add_argument("--save-snapshots", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any source fetch fails")
    args = parser.parse_args()

    sources = load_json(args.sources, [])
    errors = validate_sources(sources)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    if args.validate_only:
        print(f"Validated {len(sources)} source-watch definitions.")
        return 0

    selected = sources
    if args.source_ids:
        wanted = set(args.source_ids)
        selected = [source for source in sources if source["id"] in wanted]
        missing = sorted(wanted - {source["id"] for source in selected})
        if missing:
            print(f"Unknown source ids: {', '.join(missing)}", file=sys.stderr)
            return 2
    if args.limit is not None:
        selected = selected[: max(0, args.limit)]

    prior_state = load_json(args.state, {"schemaVersion": "1.0.0", "sources": {}})
    prior_records = prior_state.get("sources", {})
    records = dict(prior_records)
    changes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for index, source in enumerate(selected):
        record, change = fetch_source(
            source,
            prior_records.get(source["id"]),
            timeout=args.timeout,
            snapshot_dir=args.snapshot_dir,
            save_snapshots=args.save_snapshots,
        )
        records[source["id"]] = record
        if change:
            changes.append(change)
        if record.get("error"):
            failures.append({"sourceId": source["id"], "error": record["error"]})
        print(f"{source['id']}: {record.get('httpStatus')} {'ERROR' if record.get('error') else 'changed' if change else 'unchanged'}")
        if index + 1 < len(selected) and args.delay > 0:
            time.sleep(args.delay)

    run_at = utc_now()
    state = {
        "schemaVersion": "1.0.0",
        "generatedAt": run_at,
        "sourceCount": len(records),
        "sources": records,
    }
    report = {
        "schemaVersion": "1.0.0",
        "generatedAt": run_at,
        "checkedSourceCount": len(selected),
        "changedSourceCount": len(changes),
        "failedSourceCount": len(failures),
        "changes": changes,
        "failures": failures,
        "reviewRule": "A detected change is a candidate only. Update normalized data after source review and recalculation.",
    }

    if args.write_state:
        if not args.only_on_change or changes:
            write_json(args.state, state)
            write_json(args.changes, report)
        else:
            print("No content changes; state files left untouched.")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.strict and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
