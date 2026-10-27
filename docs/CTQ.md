# Critical to Quality (CTQ)

## Purpose
Translate restaurant billing requirements into measurable quality characteristics.

| Customer/staff need | Critical-to-Quality characteristic | Proposed measure | Acceptance target |
|---|---|---|---|
| Accurate bills | Calculation accuracy | Compare item totals, tax, discount, and final total with an independent calculation | Exact match to the documented rounding rule |
| Reliable order saving | Transaction integrity | Inject failures during order creation and inspect the isolated test database | No partial order remains after rollback |
| Correct menu information | Data validity | Test invalid names, prices, quantities, and availability values | Invalid input is rejected |
| Fast order lookup | Retrieval usability | Retrieve orders and verify newest-first ordering and customer names | Correct records and ordering |
| Recoverable records | Backup and recovery | Restore a backup to an isolated database and run integrity checks | Restore succeeds and record counts match |
| Usable appearance | Theme compliance | Compare available appearance choices with the SRS | All approved required themes are selectable |

## Measurement notes
Targets are proposed acceptance criteria, not measured performance results.
Record actual test evidence before declaring a CTQ passed.
