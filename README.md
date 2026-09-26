# Inteliedu

> **AI-Powered Interactive 3D Learning Platform**

Inteliedu is an educational platform that unifies interactive 3D WebGL visualizations, conversational AI tutoring (RAG + Gemini), digital learning materials, automated assessments, live interactive classrooms, voice interactions, and student analytics into a single cohesive ecosystem.

---

## Architecture Overview

Inteliedu is structured as a modular monorepo:

```
Inteliedu/
├── .agents/       # Multi-agent system guidelines, coding standards & workflows
├── docs/          # Comprehensive system, database, requirements & API documentation
├── frontend/      # React + Vite + Tailwind CSS web client
├── backend/       # Node.js + Express.js API & business logic server
├── ai/            # Gemini LLM, RAG pipeline, embeddings, and voice processing
├── threejs/       # Modular Three.js / React Three Fiber 3D scenes & loaders
├── database/      # PostgreSQL & Supabase migrations, schemas, and policies
├── storage/       # Supabase object storage assets & documentation
└── tests/         # Cross-domain test suites (frontend, backend, ai, threejs)
```

---

## Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide React
- **Backend**: Node.js, Express.js
- **AI / ML**: Gemini API, RAG (Retrieval-Augmented Generation), Text Embeddings, Vector Search
- **3D Engine**: Three.js, React Three Fiber (R3F), Drei, GLTF/GLB
- **Database & Auth**: PostgreSQL, Supabase (Auth, Database, Storage, Realtime)
- **Deployment**: Vercel (Frontend), Supabase / Cloud Services

---

## Team & Domain Ownership

| Developer | Role | Owned Directories |
| :--- | :--- | :--- |
| **Kanimozhi** | UI/UX & Frontend | `frontend/src/{components, layouts, pages, styles, assets}` |
| **Madona** | UI/UX & Frontend | `frontend/src/{features, pages/student, pages/teacher, pages/admin, services}` |
| **Prisha** | Backend | `backend/` |
| **Irene** | AI/ML | `ai/` |
| **Trivin** | 3D Graphics | `threejs/` |
| **Nidiya** | Database & Cloud | `database/`, `storage/`, Cloud configs |

---

## Getting Started

### 1. Prerequisites
- Node.js >= 18.x
- npm >= 9.x
- Supabase Account & Project
- Google Gemini API Key

### 2. Environment Setup
Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```
Fill in your Supabase credentials, database URL, and Gemini API keys.

### 3. Documentation
- [Project Overview](docs/project-overview.md)
- [Requirements Specification](docs/requirements.md)
- [System Architecture](docs/system-architecture.md)
- [Database Design](docs/database-design.md)
- [API Documentation](docs/api-documentation.md)
- [Team Roles & Matrix](docs/team-roles.md)
- [Multi-Agent Configuration](.agents/agents.md)

---

## License
Private & Confidential - Inteliedu Platform.
