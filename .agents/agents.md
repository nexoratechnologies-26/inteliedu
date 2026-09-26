# Inteliedu - Multi-Agent & Team Roles Specification

## Overview
Inteliedu is an AI-Powered Interactive 3D Learning Platform. The development team operates across clearly demarcated domains within a unified monorepo architecture. Every team member and agent persona must adhere strictly to ownership boundaries and integration contracts.

---

## Team Roster & Ownership Matrix

| Team Member | Role | Primary Domain | Owned Folders / Paths | Key Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Kanimozhi** | UI/UX & Frontend Developer | Global UI/UX, Design System, Core Pages | `frontend/src/components`<br>`frontend/src/layouts`<br>`frontend/src/pages`<br>`frontend/src/styles`<br>`frontend/src/assets` | Design tokens, reusable UI kit, layout shells, landing & generic pages |
| **Madona** | UI/UX & Frontend Developer | Feature Modules & Role Portals | `frontend/src/features/` (all submodules)<br>`frontend/src/pages/student/`<br>`frontend/src/pages/teacher/`<br>`frontend/src/pages/admin/`<br>`frontend/src/services/` | Feature state management, API service consumers, role dashboard workflows |
| **Prisha** | Backend Developer | Core Server, REST APIs, Business Logic | `backend/` | Express.js API, authentication middleware, controller endpoints, validation, database queries |
| **Irene** | AI/ML Developer | LLM Integration, RAG, NLP, Voice | `ai/` | Gemini/LLM wrappers, vector search pipeline, prompt templates, quiz/summary generators |
| **Trivin** | 3D Developer | WebGL / 3D Graphics & Interactions | `threejs/` | Three.js / R3F scene setups, 3D model loaders, interactive annotations, shaders, animations |
| **Nidiya** | Database & Cloud Developer | PostgreSQL Schema, Supabase, Cloud Ops | `database/`<br>`storage/`<br>Deployment & Cloud Configurations | Migrations, RLS security policies, seed scripts, Supabase Storage buckets, Vercel/Cloud CI |

---

## Architectural Boundaries & Cross-Domain Contracts

### 1. Frontend Boundary (`frontend/`)
- **Kanimozhi** owns the design system, base components (`Button`, `Modal`, `Navbar`, etc.), global layouts, and Tailwind design tokens.
- **Madona** consumes Kanimozhi's components and integrates business features (`features/ai-tutor`, `features/quizzes`, etc.) and dedicated user portals (`student`, `teacher`, `admin`).
- Neither frontend developer may modify backend code directly; interactions must strictly occur through HTTP/WebSocket endpoints defined by **Prisha**.

### 2. Backend Boundary (`backend/`)
- **Prisha** designs and maintains RESTful routes, authentication barriers, data validators, and business logic.
- Backend consumes **Irene's** AI module and **Nidiya's** database schemas.
- Backend does NOT serve static bundled frontend files in development and must remain decoupled from UI rendering logic.

### 3. AI / ML Boundary (`ai/`)
- **Irene** builds self-contained AI services (RAG pipeline, prompt management, voice processing, quiz generation).
- All AI features must expose clean, callable service interfaces/SDK methods that **Prisha** can invoke from the backend services layer.
- AI logic must never query the database directly without going through established database client configurations or service contracts.

### 4. 3D Graphics Boundary (`threejs/`)
- **Trivin** develops reusable Three.js / React Three Fiber components, scenes, camera controls, shaders, and label overlays.
- 3D components must be modular and exportable so **Kanimozhi** and **Madona** can embed them directly into React learning pages.
- 3D assets (`.glb`/`.gltf`) must be cataloged and loaded via standardized asset loaders.

### 5. Database & Cloud Boundary (`database/`, `storage/`)
- **Nidiya** establishes PostgreSQL schemas, migrations, stored procedures, RLS (Row Level Security) policies, and bucket storage rules.
- Team members must request schema updates through **Nidiya** rather than applying ad-hoc migrations.

---

## Collaboration & Monorepo Rules
1. **Never commit sensitive credentials**: All environment keys (`SUPABASE_KEY`, `GEMINI_API_KEY`, etc.) belong in `.env` (gitignored). Reference `.env.example`.
2. **Branching Strategy**: Each developer must branch off `main` or `develop` using their assigned prefix:
   - `feat/frontend-kanimozhi/...`
   - `feat/frontend-madona/...`
   - `feat/backend-prisha/...`
   - `feat/ai-irene/...`
   - `feat/3d-trivin/...`
   - `feat/db-nidiya/...`
3. **No Cross-Module Mutation**: Modifying files outside your assigned domain requires explicit integration alignment.
