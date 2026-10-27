# Fishbone (Ishikawa) Analysis

## Problem statement
Potential incorrect or incomplete billing records. The categories below are
hypotheses for investigation, not proof that each cause has occurred.

| Cause category | Potential contributing causes | Verification method |
|---|---|---|
| People | Repeated clicks; incorrect item or quantity entry | Observe workflow; run controlled usability checks |
| Methods | Missing submission guard; unclear retry process | Inspect billing workflow and test repeated submission |
| Software | Exceptions between order-writing steps; rounding inconsistencies | Failure-injection tests; independent total calculation |
| Data | Invalid quantities; stale menu prices; missing customer association | Validation and database-integrity tests |
| Environment | Process interruption; local database loss | Controlled tests against isolated data |
| Measurement | Missing defect categories; no measured response-time baseline | Maintain dated checksheets and reproducible measurements |

## Current control
Atomic order creation has been implemented and regression-tested.
Repeated-submission behavior and backup/recovery still require verification.
Do not label a potential cause as confirmed without evidence.
