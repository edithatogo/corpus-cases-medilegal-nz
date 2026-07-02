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
    assert "secrets.ZENODO_ACCESS_TOKEN || secrets.ZENODO_TOKEN" in workflow
    assert "ARCHIVE_CREATORS_JSON" in workflow
    assert "actions/attest-build-provenance@43d14bc2b83dec42d39ecae14e916627a18bb661" in workflow
    assert "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow
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
    assert "Build GitHub release evidence overlay" in workflow
    assert "env.PUBLICATION_MODE != 'dry-run'" in workflow
    assert "Build archive maturity report" in workflow
    assert workflow.index("Build GitHub release evidence overlay") < workflow.index(
        "Build archive maturity report"
    )
    assert workflow.index("Build archive maturity report") < workflow.index(
        "Build archive intelligence bundle"
    )
    assert workflow.index("Build archive intelligence bundle") < workflow.index(
        "Create or update GitHub release"
    )
    assert '--artifact-dir "$ARTIFACT_DIR"' in workflow
    assert "--strict" in workflow
    assert "generated/archive-intelligence/**" in workflow
    assert "archive_maturity.json" in workflow
    assert "source_observability.json" in workflow
    assert "privacy_rights_score.json" in workflow
    assert "privacy_governance.json" in workflow
    assert "redaction_exclusion_ledger.json" in workflow
    assert "anomaly_report.json" in workflow
    assert "public_claims.json" in workflow
    assert "federation_compatibility.json" in workflow
    assert "README.claims.md" in workflow


def test_security_workflows_are_present() -> None:
    workflows = {path.name for path in (ROOT / ".github/workflows").glob("*.yml")}

    assert "code_quality.yml" in workflows
    assert "codeql.yml" in workflows
    assert "scorecard.yml" in workflows
    assert "osv_scan.yml" in workflows


def test_riopa_project_sync_workflow_is_guarded_and_evidence_backed() -> None:
    workflow = (ROOT / ".github/workflows/riopa_project_sync.yml").read_text(encoding="utf-8")

    assert 'cron: "17 3 * * 1"' in workflow
    assert "workflow_dispatch:" in workflow
    assert "github.actor != 'dependabot[bot]'" in workflow
    assert "github.actor != 'renovate[bot]'" in workflow
    assert "secrets.RIOPA_PROJECT_TOKEN || secrets.GITHUB_TOKEN" in workflow
    assert "scripts/sync_riopa_project.py --apply" in workflow
    assert "scripts/sync_riopa_project.py" in workflow
    assert "riopa-project-sync-evidence" in workflow
    assert "generated/project-sync/riopa_project_sync_evidence.json" in workflow
