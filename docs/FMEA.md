# Failure Mode and Effects Analysis (FMEA)

## Project

- **Project:** Restaurant Billing System
- **Course:** BBAT104 — Fundamentals of TQM
- **Quality goal:** Q03 — Improve Usability
- **Assessment:** Living risk register; update after testing and corrective actions
- **Latest verified billing fix:** `033def2` — `fix: make billing order creation atomic`

## 1. Purpose

FMEA identifies possible failures, their causes and effects, existing controls,
and actions to reduce risk. This register prioritizes risks affecting billing
correctness, data integrity, requirements compliance, and operational recovery.

The scores below are provisional engineering estimates. Historical production
failure-frequency data is not available, so Occurrence and Detection scores
must not be interpreted as statistically measured rates.

## 2. Scoring Method

Each factor is scored from 1 to 10.

### Severity (S)

| Score | Interpretation |
|---|---|
| 1–3 | Minor inconvenience |
| 4–6 | Noticeable functional or usability impact |
| 7–8 | Significant business or data-integrity impact |
| 9–10 | Severe financial impact or potential major data loss |

### Occurrence (O)

| Score | Interpretation |
|---|---|
| 1–3 | Unlikely or requires unusual conditions |
| 4–6 | Plausible during normal operation |
| 7–8 | Likely to recur frequently |
| 9–10 | Expected or repeatedly observed |

### Detection difficulty (D)

A higher score means the failure is harder to detect before it causes harm.

| Score | Interpretation |
|---|---|
| 1–3 | Immediately apparent |
| 4–6 | Usually found during normal review |
| 7–8 | Requires targeted tests or reconciliation |
| 9–10 | Difficult to detect without specialized investigation |

**Risk Priority Number (RPN) = S × O × D**

RPN is a prioritization aid, not a probability or guarantee of failure.
A high-severity risk still requires attention even when its RPN is lower.

## 3. Risk Register

| ID | Process | Failure mode and effect | Cause / evidence | Existing controls | S | O | D | RPN | Status and action |
|---|---|---|---|---|---:|---:|---:|---:|---|
| FMEA-001 | Billing | Partial order persists after an item write or later operation fails; order history and billing data may become inconsistent. | **Confirmed defect:** billing previously committed the order header, items, totals, and completion separately. | Database validation and isolated regression tests; the new atomic operation uses one transaction. | 8 | 4 | 7 | 224 | **Corrective fix implemented.** Commit `033def2`; 34 regression tests passed, including rollback tests. Re-test the live UI and verify the database remains consistent. Reassess residual risk after that verification. |
| FMEA-002 | Billing submission | Repeated submission could create duplicate orders. | Potential failure mode; duplicate-submission behavior has not been established by the available test evidence. | Confirmation dialog; effectiveness against repeated clicks or events is unverified. | 7 | 4 | 7 | 196 | **Open / needs verification.** Test rapid repeated submission and failure/retry behavior. Add a submission guard or idempotency protection if a duplicate can be reproduced. |
| FMEA-003 | Theme usability | Required predefined custom themes may be missing or inconsistent across pages. | SRS requires multiple predefined themes; the previous audit identified this as a likely requirements gap. | Centralized theme configuration exists; full compliance is not yet demonstrated. | 5 | 6 | 6 | 180 | **Requirements verification required.** Inventory available themes and check every page. Implement missing themes or document an approved SRS change. |
| FMEA-004 | Customer management | Staff may be unable to view a customer's order history. | SRS includes customer order history where applicable; the previous audit identified a likely UI/query gap. | Customer IDs are associated with orders; a usable customer-history workflow is unverified. | 5 | 6 | 7 | 210 | **Requirements verification required.** Trace customer-to-order relationships and test the history workflow. Implement it if absent. |
| FMEA-005 | Data recovery | Local database loss or corruption may cause unrecoverable records. | SQLite is local; a verified backup-and-restore procedure has not been established by the available evidence. | SQLite persistence and database integrity checks; backup/recovery effectiveness is unverified. | 9 | 2 | 9 | 162 | **Operational control gap.** Document a safe backup procedure, restore to an isolated copy, and verify record counts and database integrity. Never run recovery experiments against the production database. |

## 4. Priority Order

Using the provisional RPN values:

1. **FMEA-001 — Partial billing transaction:** 224. Corrective fix committed; residual risk still needs validation.
2. **FMEA-004 — Customer order history:** 210. Requirements gap to verify.
3. **FMEA-002 — Duplicate submission:** 196. Potential risk; targeted reproduction test required.
4. **FMEA-003 — Custom themes:** 180. Requirements gap to verify.
5. **FMEA-005 — Backup and recovery:** 162. Operational control gap to verify.

This order sorts the provisional RPN values from highest to lowest. It does not override severity-based judgment: data recovery remains important because its potential impact is severe.

## 5. Corrective-Action Tracking

| ID | Required action | Completion evidence |
|---|---|---|
| FMEA-001 | Validate the atomic billing fix through regression tests and a controlled UI workflow. | Test output, successful multi-item order, and evidence that a failed transaction leaves no partial order. |
| FMEA-002 | Test repeated clicks, repeated events, and retry after an error. | Regression test demonstrating duplicate prevention or a documented corrective fix. |
| FMEA-003 | Compare implemented theme choices with the SRS and inspect all pages. | Theme inventory and test results for each supported theme. |
| FMEA-004 | Verify customer order-history requirements against database queries and UI behavior. | Test creating a customer, placing orders, and retrieving only that customer's orders. |
| FMEA-005 | Establish backup and restore instructions and test against an isolated database copy. | Successful restore, integrity check, and record-count comparison. |

## 6. Review and Residual Risk

Re-score each failure mode after its corrective action has been tested.
Do not mark a risk closed solely because code has changed or a document has
been written.

For every review, record:
- Review date and reviewer
- Evidence examined
- Updated S, O, D and RPN
- Corrective action status
- Residual risk and follow-up owner

## 7. Limitations

- Occurrence and Detection scores are provisional expert estimates, not derived
  from a production defect dataset.
- Potential risks must be reproduced or otherwise verified before being called
  confirmed defects.
- RPN values support prioritization but do not replace severity-based judgment.
- This register does not claim that all risks have been eliminated.
