# SQC Test Execution Checksheet

## Purpose

This checksheet records repeatable software regression checks. Test execution
results do not measure production defect frequency.

## Previously verified baseline

| Check | Expected result | Recorded result | Status |
|---|---|---|---|
| Business regression and database-integrity tests | All tests pass | 34 passed in a previous verified run | Historical baseline |
| Python source compilation | No syntax errors | Passed in a previous verified run | Historical baseline |
| Patch whitespace validation | No errors | `git diff --check` passed previously | Historical baseline |
| Production database protection | Tests do not modify `data/restaurant.db` | Metadata was verified unchanged in a previous run | Historical baseline |

## Repeatable validation commands

Run from the repository root:

```bash
PYTHONPATH=src:tests .venv314/bin/python3 -m unittest discover -s tests -v
.venv314/bin/python3 -m compileall -q src tests
git diff --check
```

For every new run, record the date, commit hash, total tests, failures, and
whether production data remained unchanged. Update the baseline only after
inspecting the actual command output.

## Statistical limitation

The existing test count is not a count of real-world defects. A valid
defect-frequency Pareto analysis requires categorized observations with
verified frequencies.
