# PDCA — Continuous Improvement Plan

## Plan
- Verify billing integrity, duplicate-submission handling, theme requirements,
  customer order-history workflow, and backup/recovery.
- Define expected outcomes and record the current commit and test baseline.

## Do
- Run regression tests in the isolated test environment.
- Reproduce suspected failures without using production data.
- Implement one corrective change at a time.

## Check
- Run the complete regression suite and source compilation.
- Inspect test output, database integrity, and `git diff --check`.
- Compare observed results with the acceptance criteria in `docs/CTQ.md`.
- Record confirmed defects separately from risks and requirements gaps.

## Act
- Keep fixes that pass validation; add regression tests for confirmed defects.
- Update FMEA severity, occurrence, and detection ratings only when evidence supports it.
- Update documentation and push each verified milestone.

## Current status
The atomic billing fix is committed. The latest verified regression baseline is
34 passing tests. Theme selection, customer-history workflow, duplicate
submission, and backup/recovery remain items to verify.
