# Workflow: Start Feature

## Purpose
Guide developers through the step-by-step process of starting, developing, and finishing a feature while respecting ownership boundaries and architectural guidelines.

---

## Step 1: Clarify Requirements & Interface Contracts
1. Review `docs/requirements.md`, `docs/system-architecture.md`, and `docs/api-documentation.md`.
2. If your feature requires cross-domain integration (e.g., Frontend requiring a new Backend API or 3D scene):
   - Check if an integration contract already exists.
   - Coordinate with the respective domain owner (e.g., Prisha for Backend, Trivin for 3D, Irene for AI).
   - Agree upon payload formats, types, and mock data before writing implementation code.

---

## Step 2: Branch Creation
1. Switch to the latest integration branch:
   ```bash
   git checkout develop
   git pull origin develop
   ```
2. Create your feature branch using your assigned prefix:
   ```bash
   git checkout -b feat/<your-name>-<feature-slug>
   ```
   *Example*: `git checkout -b feat/madona-ai-tutor-chat`

---

## Step 3: Implement Within Your Domain Directory
- Write code only within your owned directories as defined in `.agents/agents.md` and `docs/team-roles.md`.
- Keep changes modular, well-commented, and aligned with `coding-standards.md`.
- Ensure new environment variables are documented in `.env.example`.

---

## Step 4: Local Verification
- Run domain-specific unit/integration tests (`npm test` or module test script).
- Verify formatting and linting.
- Perform sanity check on responsiveness and error handling.

---

## Step 5: Commit and Open Pull Request
1. Stage and commit changes using Conventional Commits:
   ```bash
   git commit -m "feat(scope): implement feature description"
   ```
2. Push branch to remote and submit a PR against `develop`.
