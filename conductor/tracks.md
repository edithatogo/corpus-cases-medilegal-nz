# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

---

## [x] Track: Establish the HDC corpus structure, ingestion pipeline configuration, and automated Hugging Face live sync
*Link: [./conductor/tracks/hdc_sync_setup_20260613/](./conductor/tracks/hdc_sync_setup_20260613/)*
*Status: ✅ COMPLETE — Config, ingestion pipeline, exporter, HF sync, GHA workflow, 32 tests*

## [x] Track: Integrate HPDT decisions and unify the medilegal corpus schema
*Link: [./conductor/tracks/hpdt_integration/](./conductor/tracks/hpdt_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Ministry of Justice (MoJ) Tribunals decisions
*Link: [./conductor/tracks/moj_integration/](./conductor/tracks/moj_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Employment Relations Authority (ERA) decisions
*Link: [./conductor/tracks/era_integration/](./conductor/tracks/era_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Teachers Disciplinary Tribunal decisions
*Link: [./conductor/tracks/teachers_integration/](./conductor/tracks/teachers_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Royal Commissions of Inquiry and Waitangi Tribunal Reports (Near-Term)
*Link: [./conductor/tracks/royal_commissions_integration/](./conductor/tracks/royal_commissions_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Pipeline Hardening, parallel GHA sync, and multi-subset indexing
*Link: [./conductor/tracks/pipeline_hardening/](./conductor/tracks/pipeline_hardening/)*
*Status: ✅ COMPLETE — Multi-source GHA matrix workflow created (5 core sources in parallel)*

## [x] Track: Integrate Coronial Decisions and Coroners Court cases
*Link: [./conductor/tracks/coronial_integration/](./conductor/tracks/coronial_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Privacy Commissioner decisions and investigations
*Link: [./conductor/tracks/privacy_commission_integration/](./conductor/tracks/privacy_commission_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Human Rights Commission/Tribunal decisions
*Link: [./conductor/tracks/human_rights_integration/](./conductor/tracks/human_rights_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Office of the Ombudsman reports and findings
*Link: [./conductor/tracks/ombudsman_integration/](./conductor/tracks/ombudsman_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate broader Ministry of Justice (MoJ) Court cases and judicial decisions
*Link: [./conductor/tracks/moj_courts_integration/](./conductor/tracks/moj_courts_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Independent Police Conduct Authority (IPCA) reports
*Link: [./conductor/tracks/ipca_integration/](./conductor/tracks/ipca_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [x] Track: Integrate Law Commission reports and statutory recommendations
*Link: [./conductor/tracks/law_commission_integration/](./conductor/tracks/law_commission_integration/)*
*Status: ✅ COMPLETE — Config created, source registered in multi-source framework*

## [ ] Track: Implement Multi-Git and Multi-Archive Mirroring Setup
*Link: [./conductor/tracks/multi_git_archive_mirroring_20260614/](./conductor/tracks/multi_git_archive_mirroring_20260614/)*
*Status: IN PROGRESS - local mirror workflow hardening complete; GitHub secrets, live trigger verification, and external archive publication remain gated.*

## [x] Track: Monthly Dynamic Archive Publication
*Link: [./conductor/tracks/monthly_dynamic_archive_publication_20260701/](./conductor/tracks/monthly_dynamic_archive_publication_20260701/)*
*Status: ✅ COMPLETE - monthly publication workflow proved with non-zero release evidence, Hugging Face upload/readback, GitHub release assets, Zenodo draft upload, attestations, and protected production handoff.*

---

## [x] Track: GitHub RIOPA Project Synchronisation
*Link: [./conductor/tracks/github_riopa_project_synchronisation_20260701/](./conductor/tracks/github_riopa_project_synchronisation_20260701/)*
*Status: ✅ COMPLETE - project schema audit, RIOPA mirror-source fallback, sub-issue work breakdown, idempotent sync automation, operating documentation, and final in-sync evidence are complete.*

---

## [x] Track: GitHub Governance And Automation Hardening
*Link: [./conductor/tracks/github_governance_automation_hardening_20260701/](./conductor/tracks/github_governance_automation_hardening_20260701/)*
*Status: ✅ COMPLETE - governance baseline, protected Zenodo environment, branch protection, supply-chain enforcement, attestation verification, strict readiness proof, and issue/project evidence are complete.*

---

## [ ] Track: Bleeding-Edge Archive Intelligence
*Link: [./conductor/tracks/bleeding_edge_archive_intelligence_20260701/](./conductor/tracks/bleeding_edge_archive_intelligence_20260701/)*
*Status: IN PROGRESS - Phase 1 archive maturity scoring model, CLI/script entrypoints, generated local evidence, and tests are complete; next is source observability ledger hardening.*

## [ ] Track: Archive Maturity Hardening
*Link: [./conductor/tracks/archive_maturity_hardening_20260702/](./conductor/tracks/archive_maturity_hardening_20260702/)*
*Status: ✅ COMPLETE - publication-evidence overlay, strict maturity gate, workflow attachment, source observability, anomaly detection, claims generation, privacy scoring, and federation compatibility are complete.*

---

## [x] Track: Source Collection And Parser Completion
*Link: [./conductor/tracks/source_collection_parser_completion_20260701/](./conductor/tracks/source_collection_parser_completion_20260701/)*
*Status: ✅ COMPLETE - five core sources now produce validated non-zero local corpus records with deterministic exports, reconciliation ledgers, quality gates, review evidence, and GitHub issue/project evidence.*

---

## [ ] Track: Privacy, Takedown, And Redaction Governance
*Link: [./conductor/tracks/privacy_takedown_governance_20260701/](./conductor/tracks/privacy_takedown_governance_20260701/)*
*Status: NEW - plan captures privacy risk scoring, takedown/correction workflow, redaction/exclusion ledgers, and release-blocking privacy gates.*

---

## [ ] Track: Cross-Repo Archive Federation
*Link: [./conductor/tracks/cross_repo_archive_federation_20260701/](./conductor/tracks/cross_repo_archive_federation_20260701/)*
*Status: NEW - plan captures shared archive-family schemas, evidence profile versioning, federation drift reports, and RIOPA-compatible cross-repo issue/project integration.*
