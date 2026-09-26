# Inteliedu - Team Roles, Ownership & Dependency Matrix

## Team Roster

---

### 1. Kanimozhi
- **Role**: UI/UX & Frontend Developer
- **Primary Domain**: Global Design System, Shared UI Components, Base Layouts, and Core Pages
- **Owned Folders**:
  - `frontend/src/components/`
  - `frontend/src/layouts/`
  - `frontend/src/pages/` (Landing, 404, Shared static views)
  - `frontend/src/styles/`
  - `frontend/src/assets/`
  - `frontend/public/assets/`
- **Responsibilities**:
  - Design and maintain the Tailwind CSS theme, typography, color palette, and micro-interactions.
  - Build reusable UI primitives (Buttons, Modals, Cards, Dropdowns, Navbars, Sidebars, Form inputs).
  - Create responsive layouts and responsive grid wrappers.
  - Implement accessible, performant HTML5 structures.
- **Dependencies on Other Members**:
  - **Madona**: Coordinate component APIs and layout slots for feature integration.
  - **Trivin**: Canvas wrapper sizing and layout placement for 3D viewports.

---

### 2. Madona
- **Role**: UI/UX & Frontend Developer
- **Primary Domain**: Feature Modules, Role-Based Portals, and Client-Side Services
- **Owned Folders**:
  - `frontend/src/features/` (`authentication`, `dashboard`, `classes`, `learning`, `ai-tutor`, `quizzes`, `assignments`, `analytics`, `live-classroom`)
  - `frontend/src/pages/student/`
  - `frontend/src/pages/teacher/`
  - `frontend/src/pages/admin/`
  - `frontend/src/services/`
  - `frontend/src/context/`
  - `frontend/src/hooks/`
  - `frontend/src/routes/`
- **Responsibilities**:
  - Develop user portal workflows for Students, Teachers, and Admins.
  - Connect React components to backend APIs via services.
  - Build the interactive AI Tutor chat widget, Quiz submission forms, and assignment upload interfaces.
  - Manage client authentication state and route guards.
- **Dependencies on Other Members**:
  - **Kanimozhi**: Consumes base UI components and layout templates.
  - **Prisha**: Consumes backend REST and WebSocket APIs.
  - **Trivin**: Integrates 3D scenes into learning module feature views.
  - **Irene**: Subscribes to AI Tutor streaming responses.

---

### 3. Prisha
- **Role**: Backend Developer
- **Primary Domain**: Server Architecture, REST APIs, WebSocket Services, Business Logic
- **Owned Folders**:
  - `backend/` (`src/config`, `src/controllers`, `src/middleware`, `src/models`, `src/routes`, `src/services`, `src/utils`, `src/validators`, `src/server.js`)
- **Responsibilities**:
  - Maintain the Express.js server, route handlers, and request validation middleware.
  - Implement authentication middleware verifying Supabase JWTs and user roles.
  - Implement business logic for course management, assignments, quizzes, attendance, and analytics.
  - Expose clean service endpoints for frontend consumers and integrate AI module outputs.
- **Dependencies on Other Members**:
  - **Nidiya**: Schema definitions, database connection configurations, Supabase keys.
  - **Irene**: AI service invocation interfaces (RAG queries, quiz generation).
  - **Madona & Kanimozhi**: Provide stable REST endpoints according to `docs/api-documentation.md`.

---

### 4. Irene
- **Role**: AI/ML Developer
- **Primary Domain**: LLM Integration, RAG Pipelines, Vector Search, Voice Interfaces
- **Owned Folders**:
  - `ai/` (`models`, `prompts`, `rag/`, `chatbot`, `quiz-generation`, `summarization`, `voice`, `services`, `utils`)
- **Responsibilities**:
  - Build the document parsing, chunking, and vector embedding pipeline.
  - Manage system prompts, few-shot examples, and output parsing guardrails for Gemini LLM.
  - Implement RAG retrieval algorithms against PostgreSQL `pgvector`.
  - Create speech-to-text (STT) and text-to-speech (TTS) voice handlers.
  - Expose modular AI functions for Prisha's backend services.
- **Dependencies on Other Members**:
  - **Nidiya**: Vector table schemas (`pgvector` extensions and embedding dimension compatibility).
  - **Prisha**: Coordinates backend invocation hooks and payload contracts.

---

### 5. Trivin
- **Role**: 3D Developer
- **Primary Domain**: 3D Graphics, WebGL, Three.js / React Three Fiber Scenes, Model Optimizations
- **Owned Folders**:
  - `threejs/` (`components`, `scenes`, `models/`, `animations`, `controls`, `materials`, `loaders`, `interactions`, `labels`, `utils`)
- **Responsibilities**:
  - Build interactive 3D scenes for Solar System, Human Anatomy, and Engineering domains.
  - Implement orbit controls, camera transitions, lighting rigs, exploded view transforms, and 3D labels.
  - Optimize 3D models (GLTF/GLB) for low memory footprint and high WebGL frame rates (60 FPS).
  - Package 3D scenes as exportable React components for frontend consumption.
- **Dependencies on Other Members**:
  - **Nidiya**: 3D model asset storage in Supabase Storage buckets.
  - **Kanimozhi & Madona**: Align 3D canvas viewport integration and event callbacks with UI elements.

---

### 6. Nidiya
- **Role**: Database and Cloud Developer
- **Primary Domain**: PostgreSQL Schema, Supabase Configuration, Storage Buckets, Cloud Infrastructure
- **Owned Folders**:
  - `database/` (`migrations`, `schemas`, `seed`, `functions`, `policies`)
  - `storage/` (`documents`, `3d-models`, `images`, `avatars`)
  - Cloud deployment configs (Vercel, Supabase CLI, CI/CD scripts)
- **Responsibilities**:
  - Author and maintain database schemas, migrations, stored functions, and triggers.
  - Implement and test Row-Level Security (RLS) policies for data isolation.
  - Configure Supabase Storage buckets, access policies, and CDN caching rules.
  - Manage environment variables and cloud deployment configurations.
- **Dependencies on Other Members**:
  - **Prisha**: Provides database connection pooling and schema types.
  - **Irene**: Sets up `pgvector` indexing and vector column specifications.
  - **Trivin**: Provisions storage buckets for large 3D model binaries.
