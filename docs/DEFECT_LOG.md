# Defect Log

## Purpose

This log separates confirmed defects from requirements gaps and unverified risks.
An unverified risk is not counted as a confirmed defect.

## Recorded findings

| ID | Finding | Classification | Impact | Evidence / disposition |
|---|---|---|---|---|
| DEF-001 | Billing could previously leave partially written order data when order creation used separate transactions | Confirmed historical defect, fixed | Data integrity | Atomic `create_completed_order` transaction; regression tests cover rollback paths; fix commit `033def2` |
| OBS-001 | Customer order history is not exposed as an action in the inspected Customers page | SRS/UI gap to confirm | Staff may need to locate orders separately | Source inspection only; verify expected workflow against the SRS |
| OBS-002 | Settings exposes light/dark mode but no selectable predefined theme palette | SRS/UI gap | Theme requirement may not be met | Source inspection of `src/ui/pages/settings.py`; confirm intended interpretation of multiple themes |
| RISK-001 | Rapid repeated billing submission may create duplicate orders | Unverified risk, not a confirmed defect | Duplicate billing | No visible submission lock in inspected `place_order()`; reproduction test pending |
| RISK-002 | Backup and recovery procedure may be undocumented or untested | Unverified operational risk | Potential data loss | Verify using an isolated database copy only |

## Counting policy

- DEF-001 is a fixed historical defect, not an open defect unless recurrence is demonstrated.
- OBS entries are requirement-compliance observations, not confirmed runtime defects.
- RISK entries are excluded from confirmed-defect frequency counts.
- Automated test counts must not be presented as production defect counts.
