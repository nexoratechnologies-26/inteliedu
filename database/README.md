# Database & PostgreSQL Architecture (`database/`)

**Domain Owner**: Nidiya (Database and Cloud Developer)

## Overview
This module houses PostgreSQL schemas, SQL migrations, seed data, database functions (stored procedures/triggers), and Supabase Row Level Security (RLS) policies for Inteliedu.

---

## Directory Organization

```
database/
├── migrations/         # Timestamped SQL migration files (e.g., 20260926000001_initial_schema.sql)
├── schemas/            # Declarative schema definitions for all database tables
├── seed/               # Mock and initial seed data for development/testing
├── functions/          # Stored procedures, vector search functions, and trigger functions
├── policies/           # Row Level Security (RLS) SQL policies for RBAC
└── README.md
```

---

## Core Guidelines
1. **Schema Centralization**: All database modifications must be authored as SQL migrations in `migrations/` and reviewed before deployment.
2. **Row Level Security (RLS)**: Every created table must enable RLS by default.
3. **pgvector Extension**: The vector extension (`CREATE EXTENSION IF NOT EXISTS vector;`) is used for AI document embeddings in `learning_materials`.
4. **Foreign Key Integrity**: Always specify appropriate `ON DELETE` cascading rules (e.g., `CASCADE` for owned sub-items, `RESTRICT` for critical parent references).
