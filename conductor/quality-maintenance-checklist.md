# Quality & Maintenance Tooling Baseline — corpus-cases-medilegal-nz

| Tool            | Status     | Notes                                                                 |
|-----------------|------------|-----------------------------------------------------------------------|
| Vale            | ✅ Present | `.vale.ini` exists, covers `*.md` and `*.{yml,yaml}`                  |
| Markdownlint    | ✅ Present | `.markdownlint.json` created from root template                       |
| Renovate        | ✅ Present | `renovate.json` created, modelled on `cli-legislation-nz`             |
| Codecov         | ❌ Not present | `pytest-cov` in dev deps, `tool.coverage` configured. Add `codecov.yml` only after CI produces coverage XML |
| Scalene         | ❌ Not present | Not in `pyproject.toml` or dev deps. Optional — add when profiling target identified |
