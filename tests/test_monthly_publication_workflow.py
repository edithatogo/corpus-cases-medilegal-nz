from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_monthly_workflow_has_publication_guards_and_surfaces() -> None:
    workflow = (ROOT / ".github/workflows/monthly_dynamic_archive_publication.yml").read_text(
        encoding="utf-8"
    )

    assert 'cron: "30 16 1 * *"' in workflow
    assert "persist-credentials: false" in workflow
    assert "HF_TOKEN" in workflow
    assert "ZENODO_ACCESS_TOKEN" in workflow
    assert "ARCHIVE_CREATORS_JSON" in workflow
    assert "actions/attest-build-provenance@v3" in workflow
    assert "github.actor != 'dependabot[bot]'" in workflow
    assert "github.actor != 'renovate[bot]'" in workflow
    assert (
        "environment: ${{ vars.ZENODO_PROTECTED_ENVIRONMENT || 'zenodo-production' }}" in workflow
    )
    assert "publish_huggingface_release.py" in workflow
    assert "publish_zenodo_draft.py" in workflow
    assert "Build deterministic collection proof" in workflow
    assert workflow.index("Build deterministic collection proof") < workflow.index(
        "Build release evidence"
    )


def test_security_workflows_are_present() -> None:
    workflows = {path.name for path in (ROOT / ".github/workflows").glob("*.yml")}

    assert "code_quality.yml" in workflows
    assert "codeql.yml" in workflows
    assert "scorecard.yml" in workflows
    assert "osv_scan.yml" in workflows
