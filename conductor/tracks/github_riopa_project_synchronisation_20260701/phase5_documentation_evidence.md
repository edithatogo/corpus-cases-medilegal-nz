# Phase 5 Documentation And Evidence

## Summary

Phase 5 closes the RIOPA synchronisation track by making the operating contract
explicit, recording the final project-sync dry-run, and linking the repository
documentation from the public README.

## Documentation Updates

- Added `docs/riopa-project-synchronisation.md`.
- Linked the synchronisation contract from `README.md` under Distribution
  Channels.
- Documented RIOPA project `#4`, repository roadmap project `#7`, parent issue
  `#1`, and subissues `#2` through `#8`.
- Documented the hidden marker contract for `riopa-subissue-id` and
  `conductor-track-id`.
- Documented the API-safe `Mirror source: other` fallback while RIOPA lacks a
  dedicated `corpus-cases-medilegal-nz` option.
- Documented dry-run/apply commands, generated evidence location, workflow
  artifact behavior, and `RIOPA_PROJECT_TOKEN` preference.

## Final Sync Verification

Command:

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

## Issue Operating Notes

Issue `#8` is the live sync-automation follow-up issue. It records the
operating notes for:

- Dry-run and apply sync commands.
- Expected clean evidence shape.
- `RIOPA_PROJECT_TOKEN` usage.
- Dependency-update actor write guard.
- `Mirror source: other` fallback until the RIOPA board exposes a dedicated
  medilegal option.

Comment URL:

<https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/8#issuecomment-4861980645>

## Validation

Validation commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_riopa_project_sync.py tests/test_monthly_publication_workflow.py -q
uv run --frozen --python 3.12 --extra dev ruff check scripts\sync_riopa_project.py tests\test_riopa_project_sync.py tests\test_monthly_publication_workflow.py
uv run --frozen --python 3.12 --extra dev ruff format --check scripts\sync_riopa_project.py tests\test_riopa_project_sync.py tests\test_monthly_publication_workflow.py
git diff --check -- README.md docs/riopa-project-synchronisation.md conductor/tracks.md conductor/tracks/github_riopa_project_synchronisation_20260701/plan.md conductor/tracks/github_riopa_project_synchronisation_20260701/phase5_documentation_evidence.md
```

Results:

- `pytest`: `7 passed in 0.93s`.
- `ruff check`: `All checks passed!`.
- `ruff format --check`: `3 files already formatted`.
