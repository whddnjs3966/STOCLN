---
name: dev-backend
description: Start the FastAPI backend dev server on port 8000
argument-hint:
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash
---

Start the backend development server:

```bash
cd backend && source venv/Scripts/activate && uvicorn app.main:app --reload --port 8000
```

The API server runs at http://localhost:8000.
API docs available at http://localhost:8000/docs.
Report the result back to the user.
