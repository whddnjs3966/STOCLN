---
name: db-schema
description: Generate or update Supabase database schema SQL from the current Pydantic models
argument-hint:
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Write, Grep, Glob
---

Generate Supabase-compatible SQL schema by analyzing the backend models:

1. Read all Pydantic models in `backend/app/models/`
2. Read existing schema files in `backend/sql/` if they exist
3. Generate PostgreSQL DDL with:
   - Proper column types mapping from Python types
   - Primary keys, indexes, and constraints
   - Row Level Security (RLS) policies
   - Created/updated timestamps
4. Write the SQL to `backend/sql/schema.sql`

Follow Supabase conventions:
- Use `uuid` for primary keys with `gen_random_uuid()` default
- Enable RLS on all user-facing tables
- Add `created_at` and `updated_at` columns with defaults
