#!/usr/bin/env python
"""Benchmark BeautifulSoup vs selectolax parsing on HTML fixtures."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


def _fixture_html(repeats: int = 2_000) -> str:
    sentence = (
        "<article><h2>Case title</h2><p>The applicant submitted evidence on "
        '<a href="/files/1.pdf">financial records</a> and '
        '<a href="/files/2.pdf">medical notes</a>.</p>'
    )
    return "<html><body>" + (sentence * repeats) + "</body></html>"


def _benchmark_bs4(html: str, iterations: int) -> tuple[float, int, int]:
    timings: list[float] = []
    count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        soup = BeautifulSoup(html, "html.parser")
        count += len(soup.find_all(["a", "p", "article", "h2"]))
        timings.append(time.perf_counter() - start)
    return sum(timings), int(statistics.mean(timings) * 1000), count


def _benchmark_selectolax(html: str, iterations: int) -> tuple[float, int, int]:
    try:
        from selectolax.parser import HTMLParser
    except ImportError as exc:
        raise RuntimeError("selectolax is not installed") from exc

    timings: list[float] = []
    count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        parsed = HTMLParser(html)
        nodes = parsed.css("a, p, article, h2")
        count += len(nodes)
        timings.append(time.perf_counter() - start)
    return sum(timings), int(statistics.mean(timings) * 1000), count


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=2_000)
    parser.add_argument(
        "--evidence",
        default=Path(".tmp/track14_selectolax_parser_benchmark.json"),
        type=Path,
        help="Where to write benchmark evidence JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run parser benchmark and write evidence."""
    args = _build_parser().parse_args(argv)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)

    html = _fixture_html(max(500, args.repeats))
    evidence: dict[str, Any] = {
        "track": "rust_backed_tooling_hotpaths_20260614",
        "experiment": "selectolax_parser",
        "html_bytes": len(html),
        "iterations": args.iterations,
        "results": {},
    }

    bs4_duration, bs4_avg_ms, bs4_count = _benchmark_bs4(html, max(1, args.iterations))
    evidence["results"]["beautifulsoup"] = {
        "status": "measured",
        "average_latency_ms": bs4_avg_ms,
        "duration_seconds": round(bs4_duration, 6),
        "selector_count": bs4_count,
    }

    try:
        duration, avg_ms, node_count = _benchmark_selectolax(html, max(1, args.iterations))
        selectolax_status = "measured"
        selectolax_avg_ms = avg_ms
        selectolax_duration = duration
        selectolax_selector_count = node_count
    except RuntimeError as exc:
        selectolax_status = "missing_dependency"
        selectolax_avg_ms = 0
        selectolax_duration = 0.0
        selectolax_selector_count = 0
        evidence["results"]["selectolax_error"] = str(exc)

    evidence["results"]["selectolax"] = {
        "status": selectolax_status,
        "average_latency_ms": selectolax_avg_ms,
        "duration_seconds": round(selectolax_duration, 6),
        "selector_count": selectolax_selector_count,
    }
    args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
