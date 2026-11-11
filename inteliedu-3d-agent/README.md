# Inteliedu — 3D & AI Educational Video Generation Agent (Agent 5)

Modular Python + LangGraph + MCP orchestration service for generating curriculum-aligned educational 3D and supplementary AI videos for **Inteliedu** (Classes 6–12, State Board).

---

## Architecture Overview

```text
Supervisor Agent / Inteliedu Backend
        │
        ▼
FastAPI Service (/api/v1/3d-agent/*)
        │
        ▼
LangGraph 14-Node Workflow (app/agent/graph.py)
  ├─ Module 1: Topic Understanding (app/agent/topic_understanding.py)
  ├─ Module 2: Video Planning & Storyboard Validation (app/agent/video_planner.py)
  ├─ Intelligent Routing (app/agent/routing.py)
  │     Tier 1: Existing approved GLB assets (../frontend/public/assets/models/)
  │     Tier 2: Reusable Blender educational templates
  │     Tier 3: Procedural Blender STEM generation
  │     Tier 4: Supplementary Runway AI clips
  ├─ MCP Orchestration Layer (app/mcp/)
  │     ├─ BlenderMCPClient (stdio MCP SDK -> dynamic tool discovery -> CLI fallback)
  │     └─ RunwayMCPClient (Streamable HTTP / stdio MCP -> Runway REST v1 fallback)
  ├─ Module 6: FFmpeg Post-Processing (app/video/processor.py, thumbnail.py, subtitles.py)
  ├─ Module 7: Technical & Educational Validation (app/video/validator.py)
  └─ Module 8: Object Storage & Metadata Persistence (app/storage/)
```

---

## Environment Inspection Findings (Current Host)

During Phase 1 environment verification on this workstation:
- **Python**: `3.10.0` (`inteliedu-3d-agent/.venv/` prepared with `langgraph`, `mcp`, `fastapi`, `uvicorn`, `pydantic`, `httpx`, `psycopg`, `pytest`).
- **FFmpeg & FFprobe**: `8.1.1-full_build` installed and verified (`libx264`, `aac`, `ffprobe`).
- **Existing Approved 3D Assets**: 8 `.glb` assets discovered in `../frontend/public/assets/models/`, including `real_human_anatomy.glb` and `human_teacher.glb`.
- **LLM Credentials**: `GROQ_API_KEY` is configured in root `.env`; `app/config.py` loads it without exposing keys.
- **Missing External Dependencies on Host**:
  - **Blender / Blender MCP**: `C:\Program Files\Blender Foundation\Blender 4.3` contains partial `python`/`scripts` directories without `blender.exe`, and `uvx` / Blender MCP server is not installed on PATH.
  - **Runway**: Neither `RUNWAY_API_KEY` nor `RUNWAY_MCP_URL`/`RUNWAY_MCP_COMMAND` is configured yet.
  - **PostgreSQL / Supabase Storage**: `DATABASE_URL` and `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` are not configured yet; the agent automatically uses local SQLite (`generated/metadata.db`) and local object storage (`generated/storage/`) until configured.

Per project rules, when Blender or Runway is unavailable, the agent **never** fakes rendered video outputs; it preserves generated `bpy` scripts and transitions the job to `blocked` with explicit `missing_dependencies`.

---

## Setup & Running

### 1. Configure Environment
```bash
cd inteliedu-3d-agent
cp .env.example .env
# Populate BLENDER_EXECUTABLE_PATH / BLENDER_MCP_COMMAND / RUNWAY_API_KEY / SUPABASE_* as needed
```

### 2. Start API Server
```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 3. Run Automated Test Suite
```bash
.venv\Scripts\python.exe -m pytest -v
```

---

## REST API Endpoints (`/api/v1/3d-agent`)

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health and live capability availability |
| `GET` | `/api/v1/3d-agent/capabilities` | Detailed live availability report |
| `POST` | `/api/v1/3d-agent/plan` | Generate & validate storyboard without rendering |
| `POST` | `/api/v1/3d-agent/generate` | Start background video generation job (with cache dedup) |
| `GET` | `/api/v1/3d-agent/status/{job_id}` | Poll job progress, storyboard, logs, and errors |
| `GET` | `/api/v1/3d-agent/video/{video_id}` | Fetch completed video metadata |
| `GET` | `/api/v1/3d-agent/videos` | List generated educational videos |
| `POST` | `/api/v1/3d-agent/retry/{job_id}` | Retry a failed or blocked job |
| `DELETE` | `/api/v1/3d-agent/video/{video_id}` | Delete stored video and metadata |
| `GET` | `/api/v1/3d-agent/assets/{object_key}` | Serve locally stored MP4 / thumbnail / SRT files |

