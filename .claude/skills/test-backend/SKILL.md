---
name: test-backend
description: Run Python backend tests with pytest
argument-hint: [test-path]
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Edit
---

Run backend tests:

```bash
cd backend && source venv/Scripts/activate && python -m pytest $ARGUMENTS -v
```

If no arguments are provided, run all tests:
```bash
cd backend && source venv/Scripts/activate && python -m pytest -v
```

If tests fail:
1. Analyze the failure output and traceback
2. Identify root cause
3. Fix the failing code or test
4. Re-run to confirm the fix

Report test results summary to the user.
