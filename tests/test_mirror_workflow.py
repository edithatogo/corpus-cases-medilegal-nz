from pathlib import Path

from corpus_cases_medilegal_nz.mirror import classify_remote_head, mirror_sync_readiness

WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")


def test_mirror_workflow_skips_when_any_required_secret_is_missing() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert (
        'for MIRROR_URL in "$GIT_MIRROR_URL" "$GIT_MIRROR_URL_GITLAB" "$GIT_MIRROR_URL_CODEBERG"; do'
        in workflow
    )
    assert "SEEN_MIRROR_URLS[$MIRROR_URL]=1" in workflow
    assert "No mirror URLs are set, skipping mirror." in workflow
    assert 'if [ -z "$GIT_MIRROR_SSH_PRIVATE_KEY" ]; then' in workflow
    assert "GIT_MIRROR_SSH_PRIVATE_KEY is not set, skipping mirror." in workflow


def test_mirror_workflow_quotes_dynamic_shell_values_and_reports_each_target() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "git push --force --prune mirror HEAD:${{ github.ref }}" in workflow
    assert "git ls-remote mirror HEAD" in workflow
    assert 'echo "Mirrored $GIT_MIRROR_URL at $MIRROR_HEAD"' in workflow
    assert 'echo "::error::Mirror push failed for $GIT_MIRROR_URL"' in workflow
    assert 'echo "::error::$FAILURES mirror target(s) failed"' in workflow
    assert 'ssh-keyscan -t ed25519 "$HOST"' in workflow
    assert "git remote remove mirror" in workflow


def test_mirror_workflow_has_push_and_manual_dispatch_triggers() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "on:" in workflow
    assert "push:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "branches: [ main, master ]" in workflow


def test_mirror_readiness_reports_workflow_and_secret_gating() -> None:
    report = mirror_sync_readiness(
        environment={},
        root=Path(),
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["mirror_workflow_file"]["status"] == "ok"
    assert checks["mirror_push_trigger"]["status"] == "ok"
    assert checks["mirror_dispatch_trigger"]["status"] == "ok"
    assert checks["GIT_MIRROR_URL"]["status"] == "gated"
    assert checks["GIT_MIRROR_URL_GITLAB"]["status"] == "gated"
    assert checks["GIT_MIRROR_URL_CODEBERG"]["status"] == "gated"
    assert checks["GIT_MIRROR_SSH_PRIVATE_KEY"]["status"] == "gated"
    assert "GIT_MIRROR_URL" in report["blockers"]
    assert "GIT_MIRROR_URL_GITLAB" in report["blockers"]
    assert "GIT_MIRROR_URL_CODEBERG" in report["blockers"]
    assert "GIT_MIRROR_SSH_PRIVATE_KEY" in report["blockers"]


def test_mirror_readiness_strict_requires_all_mirror_targets() -> None:
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_GITLAB": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_CODEBERG": "git@codeberg.org:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "ready"
    assert report["strict_mode"] is True
    assert checks["mirror_target_set"]["status"] == "configured"


def test_mirror_readiness_strict_blocks_when_any_target_is_missing() -> None:
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_URL_GITLAB": "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git",
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["mirror_target_set"]["status"] == "gated"
    assert "mirror_target_set" in report["blockers"]


def test_remote_head_classification_flags_sha256_as_incompatible() -> None:
    assert classify_remote_head("b70b00f6642634d31299afba8976486328134a2a") == {
        "status": "ok",
        "object_format": "sha1",
        "compatible": True,
    }

    sha256 = "e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e"
    classification = classify_remote_head(sha256)

    assert classification["status"] == "incompatible"
    assert classification["object_format"] == "sha256"
    assert classification["compatible"] is False


def test_mirror_readiness_probe_blocks_sha256_gitlab_remote() -> None:
    gitlab_url = "git@gitlab.com:edithatogo/corpus-cases-medilegal-nz.git"
    codeberg_url = "git@codeberg.org:edithatogo/corpus-cases-medilegal-nz.git"
    report = mirror_sync_readiness(
        environment={
            "GIT_MIRROR_URL": gitlab_url,
            "GIT_MIRROR_URL_GITLAB": gitlab_url,
            "GIT_MIRROR_URL_CODEBERG": codeberg_url,
            "GIT_MIRROR_SSH_PRIVATE_KEY": "key",
        },
        root=Path(),
        require_complete_mirror_set=True,
        remote_heads={
            gitlab_url: "e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e",
            codeberg_url: "b70b00f6642634d31299afba8976486328134a2a",
        },
    )

    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "blocked"
    assert checks["remote_object_format"]["status"] == "blocked"
    assert checks["remote_object_format"]["incompatible_count"] == 1
    assert "remote_object_format" in report["blockers"]
    assert report["remote_probe_results"][0]["object_format"] == "sha256"
