# Skill: QA Validation

## Purpose

Verify that implementation meets acceptance criteria using real test evidence. No fake results.

## When to Use

- At the Validation stage
- After implementation is complete
- Before opening a PR for review

## Required Inputs

- Implementation output (code changes)
- Acceptance criteria from ticket
- Test suite location

## Procedure

1. **Read acceptance criteria** — List each criterion explicitly.
2. **Run the test suite** — Execute tests and capture real output.
   ```bash
   python -m pytest app/ -v
   ```
3. **Verify each criterion** — Map test results to acceptance criteria.
4. **Check edge cases** — Are edge cases covered by tests?
5. **Run Doctor if structure changed**:
   ```bash
   make sdlc-doctor
   ```
6. **Produce QA notes** — Document what was tested, what passed, what failed.

## Outputs

- Test execution results (actual terminal output)
- Criterion-by-criterion verification
- QA notes (what was tested, what was not)
- Doctor result (if applicable)

## Validation Checklist

- [ ] Tests were actually run (not assumed to pass)
- [ ] Each acceptance criterion verified individually
- [ ] Test output recorded (not summarized as "all pass")
- [ ] Edge cases identified and tested
- [ ] No known failures left unaddressed

## Failure Modes

- **Fake results** — Never write "tests pass" without running them; report actual output
- **Unmapped criteria** — Every acceptance criterion must have a corresponding test or explicit gap documented
- **Ignored failures** — If tests fail, do not proceed to review; fix the issue
- **Missing coverage** — If acceptance criteria have no tests, create them before marking validation complete
