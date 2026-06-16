# Phase 4 Execution Status

## Milestone 0 — Create execution tracker
- [x] TODO_PHASE4_EXECUTION_PLAN.md exists
- [x] Initialize status file (this file)

## Milestone 1 — Domain & Contracts package (spec scaffolding)
- [x] backend/domain/authorization.py
- [x] backend/domain/tenant.py
- [x] backend/domain/pipeline/contracts.py
- [x] backend/domain/attendance/decision.py

## Milestone 2 — Service interfaces + adapters (no endpoint change)
- [x] backend/domain/services/enrollment.py
- [x] backend/domain/services/recognition.py
- [x] backend/domain/services/attendance.py
- [x] backend/domain/services/override.py
- [x] backend/app/adapters/*_adapter.py

## Milestone 3 — Repository interfaces + tenant-aware wrappers
- [ ] backend/domain/repositories/* interfaces
- [ ] extend backend/app/repositories/* for org-scoped methods

## Milestone 4 — Face pipeline staged orchestration
- [ ] recognition_pipeline/orchestrator.py
- [ ] recognition_pipeline/stages/* wrappers
- [ ] wire into attendance_controller

## Milestone 5 — Security hardening boundary
- [ ] backend/app/api/deps.py JWT type enforcement + RBAC consistency updates
- [ ] tenant scoping tests for repositories/pipeline decisions

## Milestone 6 — Scalability plan
- [ ] jobs/attendance_jobs.py
- [ ] queues/job_client.py
