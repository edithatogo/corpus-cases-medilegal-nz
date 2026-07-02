# Phase 4 Sync Automation Evidence

Captured: 2026-07-02

## Implemented Automation

Added `scripts/sync_riopa_project.py`.

Capabilities:

- Parses stable issue markers:
  - `parent-issue`
  - `riopa-subissue-id`
  - `conductor-track-id`
- Defines the desired RIOPA sub-issue breakdown for issue `#1`.
- Detects duplicate `riopa-subissue-id` markers and blocks apply mode when duplicates exist.
- Builds an idempotent sync plan from live issue and project readbacks.
- Supports dry-run mode by default.
- Supports explicit `--apply` mode for safe issue create, close, reopen, add-to-project, status, and RIOPA mirror-source reconciliation.
- Writes JSON evidence to `generated/project-sync/riopa_project_sync_evidence.json`.

Added `.github/workflows/riopa_project_sync.yml`.

Workflow behavior:

- Runs weekly and by manual dispatch.
- Defaults to dry-run verification.
- Allows explicit manual `apply=true`.
- Guards dependency-update actors.
- Prefers `RIOPA_PROJECT_TOKEN` for user-project access and falls back to `GITHUB_TOKEN`.
- Uploads `riopa-project-sync-evidence` as a workflow artifact.

Code quality wiring:

- Added `scripts/sync_riopa_project.py` and `tests/test_riopa_project_sync.py` to the Code Quality workflow Ruff lint and format-check lists.

## Live Sync Proof

Initial dry-run detected real RIOPA project drift:

- Issues `#3`-`#8` had `mirror source: nlp-policy-nz` instead of `other`.
- Issue `#8` had RIOPA status `Done` instead of `In Progress`.

Command:

```powershell
uv run --frozen --python 3.12 --extra dev python scripts\sync_riopa_project.py --apply --output generated\project-sync\riopa_project_sync_evidence.json
```

Result:

```json
{
  "actions": [],
  "desired_subissue_count": 7,
  "duplicate_markers": {},
  "mode": "apply",
  "parent_issue": 1,
  "schema_version": "1.0.0",
  "status": "in_sync"
}
```

Follow-up dry-run:

```powershell
uv run --frozen --python 3.12 --extra dev python scripts\sync_riopa_project.py --output generated\project-sync\riopa_project_sync_evidence.json
```

Result:

```json
{
  "actions": [],
  "desired_subissue_count": 7,
  "duplicate_markers": {},
  "mode": "dry-run",
  "parent_issue": 1,
  "schema_version": "1.0.0",
  "status": "in_sync"
}
```

## Test Evidence

- `uv run --frozen --python 3.12 --extra dev pytest tests/test_riopa_project_sync.py -q`
  - Result: `4 passed`
- `uv run --frozen --python 3.12 --extra dev pytest tests/test_riopa_project_sync.py tests/test_monthly_publication_workflow.py -q`
  - Result: `6 passed`
- `uv run --frozen --python 3.12 --extra dev ruff check scripts\sync_riopa_project.py tests\test_riopa_project_sync.py`
  - Result: `All checks passed`
- `uv run --frozen --python 3.12 --extra dev ruff format --check scripts\sync_riopa_project.py tests\test_riopa_project_sync.py`
  - Result: `2 files already formatted`

## Boundary

The sync script intentionally uses `other` for RIOPA `Mirror source` until a dedicated `corpus-cases-medilegal-nz` option exists. Once that option is created, Phase 5 documentation should be updated and the script constants can move from `other` to the dedicated option id.
