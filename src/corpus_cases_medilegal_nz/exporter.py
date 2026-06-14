"""Export processed case data into multiple formats.

Supports Markdown with YAML frontmatter, plain text + JSON sidecar,
JSON Lines, and Parquet (Hive-partitioned) output.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import polars as pl
import yaml


@dataclass
class ExportableCase:
    """A case ready for export to any supported format.

    Attributes
    ----------
    case_id : str
        Unique case identifier.
    source : str
        Source/dataset name (e.g. ``"hdc"``, ``"hpdt"``).
    title : str
        Case title.
    date : str
        ISO-format date string.
    text : str
        Clean full text of the case.
    metadata : dict[str, Any]
        Arbitrary metadata keys (commissioner, parties, outcome, citations, …).
    """

    case_id: str
    source: str
    title: str
    date: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience accessors for common metadata fields
    # ------------------------------------------------------------------

    @property
    def commissioner(self) -> str:
        """Return the commissioner field from metadata, or ``""``."""
        return str(self.metadata.get("commissioner", ""))

    @property
    def parties(self) -> str:
        """Return the parties field from metadata, or ``""``."""
        return str(self.metadata.get("parties", ""))

    @property
    def outcome(self) -> str:
        """Return the outcome field from metadata, or ``""``."""
        return str(self.metadata.get("outcome", ""))

    @property
    def citations(self) -> list[str]:
        """Return the citations field from metadata, or ``[]``."""
        raw = self.metadata.get("citations", [])
        if isinstance(raw, list):
            return raw
        return [str(raw)]


# ======================================================================
# Format A — Markdown with YAML frontmatter
# ======================================================================


def export_markdown(case: ExportableCase, output_dir: Path) -> Path:
    """Write *case* as a Markdown file with YAML frontmatter.

    Parameters
    ----------
    case : ExportableCase
        The case to export.
    output_dir : Path
        Directory where the ``.md`` file will be created.

    Returns
    -------
    Path
        Path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{case.case_id}.md"

    frontmatter = {
        "case_id": case.case_id,
        "source": case.source,
        "title": case.title,
        "date": case.date,
        "commissioner": case.commissioner,
        "parties": case.parties,
        "outcome": case.outcome,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(yaml.dump(frontmatter, allow_unicode=True, sort_keys=False))
        f.write("---\n\n")
        f.write(case.text)

    return file_path


# ======================================================================
# Format B — Plain-text file + JSON sidecar metadata
# ======================================================================


def export_text_json(
    case: ExportableCase, text_dir: Path, json_dir: Path
) -> tuple[Path, Path]:
    """Write *case* as a ``.txt`` file and a ``.json`` metadata sidecar.

    Parameters
    ----------
    case : ExportableCase
        The case to export.
    text_dir : Path
        Directory for the plain-text file.
    json_dir : Path
        Directory for the JSON sidecar.

    Returns
    -------
    tuple[Path, Path]
        ``(txt_path, json_path)``.
    """
    text_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    txt_path = text_dir / f"{case.case_id}.txt"
    json_path = json_dir / f"{case.case_id}.json"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(case.text)

    sidecar = {
        "case_id": case.case_id,
        "source": case.source,
        "title": case.title,
        "date": case.date,
        "metadata": case.metadata,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2)

    return txt_path, json_path


# ======================================================================
# Format C — JSON Lines
# ======================================================================


def export_jsonl(cases: list[ExportableCase], output_path: Path) -> Path:
    """Write *cases* as a JSON Lines (``.jsonl``) file.

    Each line is a JSON object with keys ``case_id``, ``source``,
    ``title``, ``date``, ``text``, and ``metadata``.

    Parameters
    ----------
    cases : list[ExportableCase]
        Cases to export.
    output_path : Path
        Destination file path (should end with ``.jsonl``).

    Returns
    -------
    Path
        ``output_path`` (for chaining).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for case in cases:
            record = {
                "case_id": case.case_id,
                "source": case.source,
                "title": case.title,
                "date": case.date,
                "text": case.text,
                "metadata": case.metadata,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return output_path


# ======================================================================
# Format D — Apache Parquet (Hive-partitioned)
# ======================================================================


def export_parquet(
    cases: list[ExportableCase],
    output_dir: Path,
    partition_by: str = "source",
) -> Path:
    """Write *cases* as Hive-partitioned Parquet shards.

    Parameters
    ----------
    cases : list[ExportableCase]
        Cases to export.
    output_dir : Path
        Root output directory for Parquet shards.
    partition_by : str
        Column to partition by (default ``"source"``).

    Returns
    -------
    Path
        ``output_dir`` (for chaining).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if not cases:
        return output_dir

    rows = []
    for case in cases:
        rows.append(
            {
                "case_id": case.case_id,
                "source": case.source,
                "title": case.title,
                "date": case.date,
                "text": case.text,
                "metadata": json.dumps(case.metadata, ensure_ascii=False),
            }
        )

    df = pl.DataFrame(rows)
    df.write_parquet(output_dir, partition_by=[partition_by])

    return output_dir


# ======================================================================
# Unified top-level entry point
# ======================================================================


def export_all(
    cases: list[ExportableCase], processed_dir: Path
) -> dict[str, list[Path]]:
    """Export *cases* in all four supported formats.

    Sub-directories are created under *processed_dir*:

    * ``markdown/``  — Markdown with YAML frontmatter
    * ``text/``      — Plain-text files
    * ``json/``      — JSON sidecar files (paired with ``text/``)
    * ``jsonl/``     — JSON Lines file
    * ``parquet/``   — Hive-partitioned Parquet shards

    Parameters
    ----------
    cases : list[ExportableCase]
        Cases to export.
    processed_dir : Path
        Root directory under which format directories are created.

    Returns
    -------
    dict[str, list[Path]]
        Mapping of format names to lists of created file paths.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    md_dir = processed_dir / "markdown"
    txt_dir = processed_dir / "text"
    json_dir = processed_dir / "json"
    jsonl_dir = processed_dir / "jsonl"
    parquet_dir = processed_dir / "parquet"

    results: dict[str, list[Path]] = {
        "markdown": [],
        "text": [],
        "json": [],
        "jsonl": [],
        "parquet": [],
    }

    for case in cases:
        md_path = export_markdown(case, md_dir)
        results["markdown"].append(md_path)

        txt_path, json_path = export_text_json(case, txt_dir, json_dir)
        results["text"].append(txt_path)
        results["json"].append(json_path)

    jsonl_path = export_jsonl(cases, jsonl_dir / "cases.jsonl")
    results["jsonl"].append(jsonl_path)

    parquet_path = export_parquet(cases, parquet_dir)
    results["parquet"].append(parquet_path)

    return results
