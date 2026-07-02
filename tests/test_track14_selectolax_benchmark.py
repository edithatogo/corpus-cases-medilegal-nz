"""Tests for Track 14 parser benchmark script contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import benchmark_selectolax_parser as benchmark

ROOT = Path(__file__).resolve().parents[1]
WORKDIR = ROOT / ".tmp" / "track14-tests"


def _evidence_path(filename: str) -> Path:
    WORKDIR.mkdir(parents=True, exist_ok=True)
    return WORKDIR / filename


def test_selectolax_benchmark_writes_expected_result_shape() -> None:
    """Benchmark script should always write result scaffolding, even without selectolax."""
    evidence = _evidence_path("track14_selectolax_parser_benchmark.json")
    code = benchmark.main(["--iterations", "2", "--repeats", "20", "--evidence", str(evidence)])
    assert code == 0

    payload = json.loads(evidence.read_text(encoding="utf-8"))
    assert payload["track"] == "rust_backed_tooling_hotpaths_20260614"
    assert payload["experiment"] == "selectolax_parser"
    assert payload["iterations"] == 2
    assert payload["results"]["beautifulsoup"]["status"] == "measured"
    assert payload["results"]["selectolax"]["status"] in {"measured", "missing_dependency"}
