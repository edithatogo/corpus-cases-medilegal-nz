"""Build Markdown summaries from mirror readiness JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]


def _cell(value: object) -> str:
    """Return a Markdown table-safe cell value."""
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def build_markdown_report(report: JsonObject) -> str:
    """Render a concise operator report from mirror readiness output."""
    summary = report.get("mirror_target_summary", {})
    lines = [
        "# Mirror Probe Report",
        "",
        f"- Generated at: `{report.get('generated_at', 'unknown')}`",
        f"- Status: `{report.get('status', 'unknown')}`",
        f"- Blockers: `{', '.join(report.get('blockers', [])) or 'none'}`",
        f"- Configured targets: `{summary.get('configured_count', 0)}`",
        f"- Healthy targets: `{summary.get('healthy_count', 0)}`",
        f"- Blocked targets: `{summary.get('blocked_count', 0)}`",
        f"- Probe-failed targets: `{summary.get('probe_failed_count', 0)}`",
        f"- Providers: `{', '.join(summary.get('providers', [])) or 'none'}`",
        "",
        "## Targets",
        "",
        "| Provider | Status | Object format | HEAD | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for target in report.get("mirror_targets", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(target.get("provider")),
                    _cell(target.get("status")),
                    _cell(target.get("object_format")),
                    _cell(target.get("head")),
                    _cell(target.get("reason")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Next Actions", ""])
    next_actions = report.get("next_actions", [])
    if next_actions:
        lines.extend(f"- {action}" for action in next_actions)
    else:
        lines.append("- None. Strict mirror readiness is ready.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run the report generator."""
    parser = argparse.ArgumentParser(description="Build a mirror probe Markdown report.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    ns = parser.parse_args(argv)

    report = json.loads(ns.input.read_text(encoding="utf-8"))
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    ns.output.write_text(build_markdown_report(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
