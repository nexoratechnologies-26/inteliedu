# Inteliedu - Requirements Specification

## 1. Functional Requirements

### FR-01: Authentication & Authorization
- Secure sign-up, sign-in, password reset, and OAuth providers managed through Supabase Auth.
- Role-based access control (RBAC) with three primary roles: `student`, `teacher`, `admin`.
- JWT token handling with automatic refresh and route guard protection.

### FR-02: Student Dashboard
- Overview of enrolled courses, upcoming classes, pending assignments, and recent quiz scores.
- Quick-launch cards for continuing 3D lessons and AI tutor sessions.
- Personal study streak, completion metrics, and personalized recommendations.

### FR-03: Teacher Dashboard
- Class management overview, active student count, and attendance statistics.
- Direct links to launch Live Classrooms with 3D model synchronization.
- Quick tools for AI-powered quiz creation, assignment grading, and material uploads.

### FR-04: Admin Dashboard
- System-wide user directory (students, teachers, staff) with role assignment and account state control.
- Course catalog audit and platform usage analytics.
- Storage capacity monitoring and system configuration.

### FR-05: Class Management
- Creation of classes, courses, sections, and lesson schedules.
- Student enrollment via direct invitation or class code.
- Role-specific access to class roster, announcements, and syllabus.

### FR-06: Learning Materials Management
- Support for uploading and organizing documents (PDF, DOCX, Markdown, video links).
- Categorization by subject, grade level, topic, and associated 3D scene.
- Document indexing pipeline feeding into the RAG vector store.

### FR-07: Interactive 3D Learning
- Interactive WebGL canvas powered by Three.js and React Three Fiber.
- Domain-specific curated model catalogs:
  - **Solar System**: Planetary orbits, surface textures, comparative scales.
  - **Human Anatomy**: Organ layers, skeletal/muscular systems, cardiovascular flows.
  - **Engineering**: Mechanical engines, structural bridge loads, interactive parts breakdown.
- User controls: Orbit, pan, zoom, explode parts, x-ray view, clickable informational hotspots/labels.

### FR-08: AI Tutor
- Real-time conversational AI tutor interface embedded within lesson views.
- Contextual understanding of the specific lesson, topic, and active 3D model.
- Step-by-step Socratic explanations, hints, and simplified summaries.

### FR-09: Retrieval-Augmented Generation (RAG)
- Document processing pipeline: chunking, embedding generation using Gemini Embeddings API.
- Semantic vector retrieval backed by PostgreSQL `pgvector` / Supabase.
- Strict factual grounding to prevent hallucinations when answering syllabus questions.

### FR-10: Voice Interaction
- Speech-to-text (STT) for hands-free student queries to the AI tutor.
- Text-to-speech (TTS) with natural audio playback for tutor responses.
- Audio toggle controls with real-time waveform visualization.

### FR-11: Quiz System
- Manual quiz creation by teachers and automated AI quiz generation from lesson text.
- Multiple choice, true/false, fill-in-the-blank, and 3D-model pin identification questions.
- Instant automated grading, attempt history, and detailed answer explanations.

### FR-12: Assignment System
- Assignment publishing with deadlines, attachments, and rubric specifications.
- Student submission portal (text, file upload, or interactive 3D snapshot).
- Teacher grading portal with inline feedback and score publication.

### FR-13: Live Classroom
- Real-time virtual classroom with video, audio, and chat via WebSockets / WebRTC.
- Synchronized 3D viewer: Teacher can rotate/explode a model and mirror the viewpoint to students.
- Screen sharing, hand-raise queue, and in-class polls.

### FR-14: Attendance Tracking
- Automated logging of student join/leave timestamps during live sessions.
- Manual attendance override for teachers.
- Attendance percentage reporting per student and per class.

### FR-15: Student Analytics
- Visual learning analytics: time spent per module, 3D interaction engagement, quiz mastery radar charts.
- Identification of struggling topics with AI recommendations for remedial review.
- Teacher reporting dashboard for class-wide performance trends.

---

## 2. Non-Functional Requirements

### NFR-01: Performance & 3D Frame Rate
- Maintain a minimum of 60 FPS for standard 3D scenes on modern desktop and laptop GPUs.
- Progressive level-of-detail (LOD) and asset streaming for heavy 3D assets to keep initial load times under 3 seconds.

### NFR-02: Security & Privacy
- Zero plaintext storage of passwords or API keys.
- Row-Level Security (RLS) enforced across all database tables.
- HTTPS encryption in transit and AES-256 encryption at rest.

### NFR-03: Scalability & Reliability
- Stateless Node.js/Express backend capable of horizontal scaling.
- Database connection pooling and vector index optimization.
- CDN caching for static frontend assets and 3D GLTF binaries.

### NFR-04: Usability & Accessibility
- Clean, modern, responsive UI adaptable from 13-inch laptops to large desktop monitors.
- WCAG 2.1 AA compliance for text contrast, keyboard navigation, and screen reader labels.
