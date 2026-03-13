---
name: lint-frontend
description: Run ESLint and TypeScript type checking on the frontend
argument-hint:
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Edit
---

Run lint and type checks on the frontend:

```bash
cd frontend && npx next lint && npx tsc --noEmit
```

If errors are found:
1. Read the error output
2. Fix all lint and type errors in the source files
3. Re-run to verify all errors are resolved

Report a summary of issues found and fixed to the user.
