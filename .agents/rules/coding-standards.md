# Inteliedu - Coding Standards

## 1. General Principles
- Use clean, self-documenting code with meaningful naming conventions.
- Maintain consistent indentation (2 spaces for JS/JSX/JSON/CSS/SQL).
- Keep functions small, focused, and pure where practical.
- Provide JSDoc / Docstring comments for complex business logic, public service functions, and 3D math calculations.

---

## 2. Frontend (React + Vite + Tailwind CSS)
- **Component Structure**: PascalCase for component files (e.g., `Button.jsx`, `AiTutorChat.jsx`).
- **Hooks & Utilities**: camelCase for custom hooks (`useAuth.js`) and helper utilities (`formatDate.js`).
- **Component Organization**:
  - Keep components modular, reusable, and decoupled from raw API calls.
  - Call API endpoints through dedicated service modules in `frontend/src/services/`.
  - Feature-specific UI resides inside `frontend/src/features/<feature_name>/components/`.
- **Styling**:
  - Use Tailwind CSS utility classes systematically.
  - Follow the design palette and typography defined in global styles.
  - Avoid inline style attributes unless dynamic 3D canvas coordinates or runtime CSS variables demand it.

---

## 3. Backend (Node.js + Express.js)
- **Layered Architecture**:
  - `routes/` -> Route declarations, HTTP verbs, path definitions.
  - `validators/` -> Input validation schemas (e.g., Joi/Zod/express-validator).
  - `middleware/` -> Auth guard, role checking, error handling, rate limiting.
  - `controllers/` -> Request parsing, response formatting, status codes.
  - `services/` -> Core business logic, external API integrations, AI service triggers.
  - `models/` -> Data access layers or ORM/query wrappers.
  - `config/` -> Environment configuration loaders.
- **Error Handling**:
  - Never let unhandled promise rejections crash the server.
  - Pass errors to the centralized `errorHandler` middleware.
  - Always return consistent JSON response envelopes:
    ```json
    {
      "success": false,
      "message": "Error description",
      "errors": []
    }
    ```

---

## 4. AI & Machine Learning (`ai/`)
- **Modularity**:
  - Structure pipelines into logical sub-steps: document loader -> text processing -> embeddings -> retrieval -> generation.
  - Parameterize prompt templates to avoid brittle string concatenations.
  - Abstract LLM vendor calls behind generic adapter interfaces.
- **Fail-safes**:
  - Implement retry mechanisms with exponential backoff for external LLM API rate limits.
  - Include guardrails to validate and sanitize AI-generated structured outputs (such as quiz JSON).

---

## 5. 3D Graphics (`threejs/`)
- **Performance & Asset Management**:
  - Optimize polygon counts and compress textures (WebP, KTX2) where applicable.
  - Lazy load heavy 3D GLB/GLTF assets and display loading progress indicators.
  - Properly dispose of geometries, materials, and textures on component unmount to prevent WebGL memory leaks.
- **Reusability**:
  - Keep 3D scene wrappers isolated from page layout logic.
  - Standardize camera controls, lighting setups, and annotation pins.

---

## 6. Database (`database/` & Supabase)
- **Naming Conventions**:
  - Table names: `snake_case` plural (e.g., `users`, `learning_materials`, `quiz_attempts`).
  - Column names: `snake_case` (e.g., `created_at`, `student_id`).
  - Primary keys: UUID `id` with `DEFAULT gen_random_uuid()`.
  - Foreign keys: `<singular_table>_id` (e.g., `course_id`, `user_id`).
- **Security**:
  - Enable Row Level Security (RLS) on all public tables.
  - Define clear policies for `SELECT`, `INSERT`, `UPDATE`, `DELETE` based on authenticated user roles.
