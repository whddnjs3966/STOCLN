---
name: build-frontend
description: Build the Next.js frontend for production and report any errors
argument-hint:
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash, Read, Edit
---

Run a production build of the frontend:

```bash
cd frontend && npm run build
```

If the build fails:
1. Read the error output carefully
2. Identify the failing file(s) and line number(s)
3. Fix TypeScript or build errors
4. Re-run the build to verify

Report the build result (success/failure + route summary) to the user.
