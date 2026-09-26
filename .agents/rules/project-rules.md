# Inteliedu - Project Rules

## Core Principles
1. **Single Monorepo Architecture**:
   - All modules (`frontend`, `backend`, `ai`, `threejs`, `database`, `storage`, `tests`, `docs`) reside in one coordinated repository.
   - Do not spin up separate isolated git repositories for individual sub-teams.

2. **Strict Module Separation & Loose Coupling**:
   - Frontend communicates with Backend solely through documented REST/WebSocket APIs.
   - AI functionality is modular and exposed as reusable services.
   - 3D graphics components are exportable and composable within React.
   - Database schemas, migrations, and storage policies are centralized in `database/` and `storage/`.

3. **Zero Secrets in Version Control**:
   - Never commit `.env` files, API keys, database credentials, or secret tokens.
   - Always update `.env.example` with clear placeholder variable names whenever new environment configurations are introduced.

4. **Team Ownership Integrity**:
   - Each developer respects their owned domain:
     - Kanimozhi (`frontend/src/{components,layouts,pages,styles,assets}`)
     - Madona (`frontend/src/{features,pages/student,pages/teacher,pages/admin,services}`)
     - Prisha (`backend/`)
     - Irene (`ai/`)
     - Trivin (`threejs/`)
     - Nidiya (`database/`, `storage/`, cloud configs)
   - Do not edit another developer's module unless an explicit integration contract or PR review requires it.

5. **Design & UX Excellence**:
   - All user interfaces must provide responsive, accessible, dynamic, and visually engaging experiences.
   - Reusable design tokens and Tailwind CSS classes must be centralized.

6. **Defensive Programming & Validation**:
   - Validate all user inputs on both frontend forms and backend controllers/validators.
   - Use standard HTTP status codes, structured JSON error formats, and centralized error middleware.
