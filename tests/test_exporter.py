"""Tests for the ``exporter`` module."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import pytest
import yaml

from corpus_cases_medilegal_nz.exporter import (
    ExportableCase,
    export_all,
    export_jsonl,
    export_markdown,
    export_parquet,
    export_text_json,
)


@pytest.fixture
def sample_case() -> ExportableCase:
    """Return a realistic mock ``ExportableCase``."""
    return ExportableCase(
        case_id="HDC-2024-001",
        source="hdc",
        title="A Complaint About District Health Board",
        date="2024-03-15",
        text=(
            "This is the full text of the decision.\n"
            "It contains multiple paragraphs.\n\n"
            "The Commissioner found the DHB in breach."
        ),
        metadata={
            "commissioner": "Commissioner Paterson",
            "parties": "Mr A v Waitemata DHB",
            "outcome": "Breach",
            "citations": ["[2024] NZHDC 1", "[2024] NZHDC 2"],
        },
    )


@pytest.fixture
def sample_cases(sample_case: ExportableCase) -> list[ExportableCase]:
    """Return a list of two exportable cases from different sources."""
    case2 = ExportableCase(
        case_id="HPDT-2024-042",
        source="hpdt",
        title="A Professional Discipline Matter",
        date="2024-06-01",
        text="This is a different decision from the HPDT.",
        metadata={
            "commissioner": "",
            "parties": "Dr B v Council",
            "outcome": "Struck off",
            "citations": [],
        },
    )
    return [sample_case, case2]


@pytest.fixture
def case_empty_text() -> ExportableCase:
    """Return a case with empty text and minimal metadata."""
    return ExportableCase(
        case_id="EMPTY-001",
        source="test",
        title="Empty Text Case",
        date="2024-01-01",
        text="",
        metadata={},
    )


class TestExportableCase:
    """Tests for the ``ExportableCase`` dataclass and its properties."""

    def test_commissioner_property(self, sample_case: ExportableCase) -> None:
        """Should return the commissioner from metadata."""
        assert sample_case.commissioner == "Commissioner Paterson"

    def test_commissioner_fallback(self, case_empty_text: ExportableCase) -> None:
        """Should return empty string when commissioner is missing."""
        assert case_empty_text.commissioner == ""

    def test_parties_property(self, sample_case: ExportableCase) -> None:
        """Should return the parties from metadata."""
        assert sample_case.parties == "Mr A v Waitemata DHB"

    def test_parties_fallback(self, case_empty_text: ExportableCase) -> None:
        """Should return empty string when parties is missing."""
        assert case_empty_text.parties == ""

    def test_outcome_property(self, sample_case: ExportableCase) -> None:
        """Should return the outcome from metadata."""
        assert sample_case.outcome == "Breach"

    def test_outcome_fallback(self, case_empty_text: ExportableCase) -> None:
        """Should return empty string when outcome is missing."""
        assert case_empty_text.outcome == ""

    def test_citations_list(self, sample_case: ExportableCase) -> None:
        """Should return citations list from metadata."""
        assert sample_case.citations == ["[2024] NZHDC 1", "[2024] NZHDC 2"]

    def test_citations_fallback(self, case_empty_text: ExportableCase) -> None:
        """Should return empty list when citations is missing."""
        assert case_empty_text.citations == []

    def test_citations_string_coerced(self) -> None:
        """Should wrap a single citation string in a list."""
        case = ExportableCase(
            case_id="X", source="x", title="x",
            date="2024-01-01", text="x",
            metadata={"citations": "[2024] NZDC 1"},
        )
        assert case.citations == ["[2024] NZDC 1"]


class TestExportMarkdown:
    """Tests for ``export_markdown``."""

    def test_creates_md_file(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Should create a .md file at the expected path."""
        out = export_markdown(sample_case, tmp_path)
        assert out == tmp_path / "HDC-2024-001.md"
        assert out.is_file()

    def test_yaml_frontmatter(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Frontmatter should be valid YAML and contain expected keys."""
        out = export_markdown(sample_case, tmp_path)
        content = out.read_text(encoding="utf-8")
        assert content.startswith("---\n")

        parts = content.split("---\n", 2)
        assert len(parts) >= 3
        front = yaml.safe_load(parts[1])
        assert front["case_id"] == "HDC-2024-001"
        assert front["source"] == "hdc"
        assert front["title"] == "A Complaint About District Health Board"
        assert front["date"] == "2024-03-15"
        assert front["commissioner"] == "Commissioner Paterson"
        assert front["parties"] == "Mr A v Waitemata DHB"
        assert front["outcome"] == "Breach"

    def test_body_content(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Body after frontmatter should be the case text."""
        out = export_markdown(sample_case, tmp_path)
        content = out.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        body = parts[2]
        assert sample_case.text in body

    def test_empty_text(
        self, case_empty_text: ExportableCase, tmp_path: Path
    ) -> None:
        """Should handle empty text gracefully."""
        out = export_markdown(case_empty_text, tmp_path)
        content = out.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        assert parts[2].strip() == ""

class TestExportTextJson:
    """Tests for ``export_text_json``."""

    def test_creates_txt_and_json(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Should create both .txt and .json files."""
        text_dir = tmp_path / "text"
        json_dir = tmp_path / "json"
        txt_path, json_path = export_text_json(sample_case, text_dir, json_dir)

        assert txt_path == text_dir / "HDC-2024-001.txt"
        assert json_path == json_dir / "HDC-2024-001.json"
        assert txt_path.is_file()
        assert json_path.is_file()

    def test_text_content(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Txt file should contain the exact case text."""
        txt_path, _ = export_text_json(
            sample_case, tmp_path / "text", tmp_path / "json"
        )
        assert txt_path.read_text(encoding="utf-8") == sample_case.text

    def test_json_sidecar(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """JSON sidecar should have expected structure."""
        _, json_path = export_text_json(
            sample_case, tmp_path / "text", tmp_path / "json"
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["case_id"] == "HDC-2024-001"
        assert data["source"] == "hdc"
        assert data["title"] == "A Complaint About District Health Board"
        assert data["date"] == "2024-03-15"
        assert data["metadata"]["commissioner"] == "Commissioner Paterson"

    def test_empty_text(
        self, case_empty_text: ExportableCase, tmp_path: Path
    ) -> None:
        """Should handle empty text."""
        txt_path, json_path = export_text_json(
            case_empty_text, tmp_path / "text", tmp_path / "json"
        )
        assert txt_path.read_text(encoding="utf-8") == ""
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["metadata"] == {}


class TestExportJsonl:
    """Tests for ``export_jsonl``."""

    def test_creates_jsonl(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create a .jsonl file with one JSON object per line."""
        out_path = tmp_path / "cases.jsonl"
        result = export_jsonl(sample_cases, out_path)
        assert result == out_path
        assert out_path.is_file()

    def test_one_object_per_line(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Each line should be a valid JSON object."""
        out_path = tmp_path / "cases.jsonl"
        export_jsonl(sample_cases, out_path)
        lines = out_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            obj = json.loads(line)
            assert "case_id" in obj
            assert "source" in obj
            assert "title" in obj
            assert "date" in obj
            assert "text" in obj
            assert "metadata" in obj

    def test_content_roundtrip(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Parsed objects should match original case data."""
        out_path = tmp_path / "cases.jsonl"
        export_jsonl(sample_cases, out_path)
        lines = out_path.read_text(encoding="utf-8").strip().splitlines()
        for case, line in zip(sample_cases, lines, strict=False):
            obj = json.loads(line)
            assert obj["case_id"] == case.case_id
            assert obj["source"] == case.source
            assert obj["title"] == case.title
            assert obj["date"] == case.date
            assert obj["text"] == case.text
            assert obj["metadata"] == case.metadata

    def test_empty_list(self, tmp_path: Path) -> None:
        """Should create an empty file when cases list is empty."""
        out_path = tmp_path / "cases.jsonl"
        export_jsonl([], out_path)
        assert out_path.is_file()
        assert out_path.read_text(encoding="utf-8").strip() == ""


class TestExportParquet:
    """Tests for ``export_parquet``."""

    def test_creates_partitioned_output(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create Hive-partitioned Parquet shards."""
        export_parquet(sample_cases, tmp_path / "parquet")
        parquet_dir = tmp_path / "parquet"
        assert parquet_dir.is_dir()
        assert (parquet_dir / "source=hdc").is_dir()
        assert (parquet_dir / "source=hpdt").is_dir()

    def test_roundtrip_with_polars(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Data written should be readable back with polars."""
        parquet_dir = tmp_path / "parquet"
        export_parquet(sample_cases, parquet_dir)
        df = pl.read_parquet(parquet_dir)
        assert df.height == 2
        assert set(df["case_id"].to_list()) == {
            "HDC-2024-001", "HPDT-2024-042"
        }
        assert set(df["source"].to_list()) == {"hdc", "hpdt"}

    def test_custom_partition_by(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should partition by a custom column when specified."""
        export_parquet(
            sample_cases, tmp_path / "parquet_date", partition_by="date"
        )
        parquet_dir = tmp_path / "parquet_date"
        assert (parquet_dir / "date=2024-03-15").is_dir()
        assert (parquet_dir / "date=2024-06-01").is_dir()

    def test_empty_list(self, tmp_path: Path) -> None:
        """Should create empty parquet dir when list is empty."""
        parquet_dir = tmp_path / "parquet_empty"
        export_parquet([], parquet_dir)
        assert parquet_dir.is_dir()


class TestExportAll:
    """Tests for ``export_all``."""

    def test_creates_all_format_dirs(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create sub-directories for each format."""
        export_all(sample_cases, tmp_path / "processed")
        processed = tmp_path / "processed"
        assert (processed / "markdown").is_dir()
        assert (processed / "text").is_dir()
        assert (processed / "json").is_dir()
        assert (processed / "jsonl").is_dir()
        assert (processed / "parquet").is_dir()

    def test_returns_all_formats(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Result dict should contain keys for all formats."""
        result = export_all(sample_cases, tmp_path / "processed")
        assert set(result.keys()) == {
            "markdown", "text", "json", "jsonl", "parquet"
        }

    def test_markdown_files_created(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create a .md file per case."""
        result = export_all(sample_cases, tmp_path / "processed")
        assert len(result["markdown"]) == 2
        for p in result["markdown"]:
            assert p.suffix == ".md"
            assert p.is_file()

    def test_text_and_json_files_created(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create a .txt and .json file per case."""
        result = export_all(sample_cases, tmp_path / "processed")
        assert len(result["text"]) == 2
        assert len(result["json"]) == 2
        for p in result["text"]:
            assert p.suffix == ".txt"
            assert p.is_file()
        for p in result["json"]:
            assert p.suffix == ".json"
            assert p.is_file()

    def test_jsonl_file_created(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create a single .jsonl file."""
        result = export_all(sample_cases, tmp_path / "processed")
        assert len(result["jsonl"]) == 1
        assert result["jsonl"][0].suffix == ".jsonl"
        assert result["jsonl"][0].is_file()

    def test_parquet_dir_created(
        self, sample_cases: list[ExportableCase], tmp_path: Path
    ) -> None:
        """Should create a parquet directory."""
        result = export_all(sample_cases, tmp_path / "processed")
        assert len(result["parquet"]) == 1
        assert result["parquet"][0].is_dir()

    def test_single_case(
        self, sample_case: ExportableCase, tmp_path: Path
    ) -> None:
        """Should handle a single case."""
        result = export_all([sample_case], tmp_path / "processed")
        assert len(result["markdown"]) == 1
        assert len(result["text"]) == 1
        assert len(result["json"]) == 1
        assert len(result["jsonl"]) == 1
        assert len(result["parquet"]) == 1

