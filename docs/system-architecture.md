# Inteliedu - System Architecture

## 1. High-Level Architecture Overview

Inteliedu adopts a clean, layered, and decoupled client-server architecture designed for high scalability, real-time interactive 3D rendering, and intelligent retrieval-augmented generation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND LAYER                                  │
│             React + Vite + Tailwind CSS + React Three Fiber                 │
│   ┌───────────────────────┬───────────────────────┬─────────────────────┐   │
│   │   Student Portal      │    Teacher Portal     │    Admin Portal     │   │
│   └───────────────────────┴───────────────────────┴─────────────────────┘   │
│   ┌───────────────────────┬───────────────────────┬─────────────────────┐   │
│   │ 3D Interactive Viewer │ AI Tutor Chat & Voice │ Live Classroom View │   │
│   └───────────────────────┴───────────────────────┴─────────────────────┘   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS (REST) / WSS (Realtime)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND API LAYER                                │
│                          Node.js + Express.js                               │
│  ┌────────────────────┬────────────────────┬─────────────────────────────┐  │
│  │ Auth & RBAC Guard  │ Controllers & API  │ Validation & Middleware     │  │
│  └────────────────────┴────────────────────┴─────────────────────────────┘  │
│  ┌────────────────────┬────────────────────┬─────────────────────────────┐  │
│  │ Business Services  │ WebSocket Server   │ Orchestration Layer         │  │
│  └────────────────────┴────────────────────┴─────────────────────────────┘  │
└───────────────┬──────────────────────┬──────────────────────┬───────────────┘
                │                      │                      │
                ▼                      ▼                      ▼
┌────────────────────────┐┌────────────────────────┐┌─────────────────────────┐
│       AI ENGINE        ││       3D ASSETS        ││        DATABASE         │
│  Gemini API + RAG +    ││  Three.js / Drei /     ││  PostgreSQL / pgvector  │
│  Vector Embeddings     ││  GLTF & GLB Models     ││  Supabase Client        │
└───────────────┬────────┘└────────────┬───────────┘└─────────────┬───────────┘
                │                      │                          │
                ▼                      ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE & CLOUD                              │
│  ┌─────────────────────┬─────────────────────┬───────────────────────────┐  │
│  │ Supabase Auth & DB  │  Supabase Storage   │ Gemini 1.5 / LLM APIs     │  │
│  └─────────────────────┴─────────────────────┴───────────────────────────┘  │
│  ┌─────────────────────┬─────────────────────┬───────────────────────────┐  │
│  │ Vercel (FE Hosting) │ Node Cloud Runtime  │ WebRTC Signaling          │  │
│  └─────────────────────┴─────────────────────┴───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Responsibilities

### Layer 1: Frontend Client (`frontend/`)
- **Technology**: React 18+, Vite, Tailwind CSS, Lucide Icons, React Three Fiber (R3F), Drei.
- **Responsibilities**:
  - Delivers dynamic, accessible, and responsive user interfaces for Students, Teachers, and Admins.
  - Hosts the 3D Canvas viewport with orbit controls, interactive pins, and exploded views.
  - Manages client-side state, user sessions, theme tokens, and local optimistic updates.
  - Consumes Backend REST APIs via Axios/Fetch services and subscribes to real-time events.

### Layer 2: Backend Application Server (`backend/`)
- **Technology**: Node.js, Express.js, WebSocket/Socket.io.
- **Responsibilities**:
  - Serves as the central security and orchestration gateway.
  - Enforces RBAC permissions and validates request payloads.
  - Connects frontend consumers to internal domain services:
    - AI Orchestration (calling `ai/` pipelines)
    - Learning Management business logic (courses, classes, submissions)
    - Assessment & Grading workflows
    - Real-time signaling for live classrooms

### Layer 3: AI & Machine Learning Services (`ai/`)
- **Technology**: Google Gemini API, LangChain / LlamaIndex principles, Sentence Transformers / Gemini Embeddings.
- **Responsibilities**:
  - Parses uploaded PDF/text learning materials into normalized semantic chunks.
  - Generates high-dimensional vector embeddings and queries PostgreSQL `pgvector`.
  - Performs retrieval-augmented prompt compilation to generate grounded tutor responses and automated quizzes.
  - Handles speech-to-text transcription and text-to-speech synthesis pipelines.

### Layer 4: 3D Visualization System (`threejs/`)
- **Technology**: Three.js, React Three Fiber, Drei, GLTF Loader, DRACO compression.
- **Responsibilities**:
  - Modular scene builders for distinct domains: Solar System, Human Anatomy, Engineering Mechanics.
  - Interactive annotation systems, layer peeling, raycasting hotspots, and lighting/shadow rigs.
  - Exportable component wrappers seamlessly imported into React feature pages.

### Layer 5: Database, Storage & Cloud (`database/`, `storage/`)
- **Technology**: Supabase (PostgreSQL 15+, `pgvector`, Auth, Storage, Realtime), Vercel.
- **Responsibilities**:
  - Relational persistence with foreign keys, composite indexes, and strict Row Level Security (RLS).
  - Secure object storage buckets for binary 3D assets (`.glb`/`.gltf`), course documents, and avatar images.
  - Real-time change streams for notifications, live attendance, and collaborative classroom state.

---

## 3. Data Flow Workflows

### A. RAG-Powered AI Tutor Query Flow
```
1. Student asks question on 3D Lesson Page (Text or Voice)
2. Frontend sends query + lesson_id to Backend /api/ai/chat
3. Backend calls AI RAG Service:
   a. Converts question to embedding vector
   b. Performs similarity search against database (Supabase pgvector) for lesson documents
   c. Constructs grounded context prompt with retrieved syllabus chunks
   d. Calls Gemini API for completion
4. Backend streams or returns response to Frontend AI Tutor widget
```

### B. Interactive 3D Model Loading Flow
```
1. Student opens "Human Anatomy: Cardiovascular System"
2. Frontend loads 3D Component Wrapper from `threejs/scenes/`
3. Scene component fetches optimized GLTF/GLB asset from Supabase Storage CDN
4. Canvas renders interactive model with predefined camera waypoints and interactive labels
5. User clicks on "Aorta" label -> Triggers context update in AI Tutor sidebar
```
