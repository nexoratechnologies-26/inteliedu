# Inteliedu - Git & Branching Workflow

## 1. Branch Strategy

The repository follows a feature branch model anchored on `main` and `develop`:

- `main`: Production-ready, stable codebase.
- `develop`: Main integration branch for active development.
- `feat/<owner>-<feature-name>`: Feature branch owned by an individual developer.
- `fix/<owner>-<bug-name>`: Bug fix branch.
- `docs/<owner>-<doc-name>`: Documentation update branch.

### Ownership Branch Prefixes:
- **Kanimozhi**: `feat/kanimozhi-...`
- **Madona**: `feat/madona-...`
- **Prisha**: `feat/prisha-...`
- **Irene**: `feat/irene-...`
- **Trivin**: `feat/trivin-...`
- **Nidiya**: `feat/nidiya-...`

---

## 2. Commit Message Convention
Use Conventional Commits format:
`<type>(<scope>): <subject>`

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process, dependencies, or auxiliary tools

### Scopes:
- `frontend`, `components`, `features`, `backend`, `api`, `ai`, `rag`, `threejs`, `db`, `storage`, `docs`

### Examples:
- `feat(frontend): create responsive navbar and sidebar layout`
- `feat(ai): integrate gemini embedding pipeline for course notes`
- `fix(backend): handle expired jwt tokens gracefully in auth middleware`
- `feat(threejs): implement orbit controls and pin labels for solar system scene`
- `feat(db): add migration for quiz_attempts and submissions tables`

---

## 3. Pull Request Guidelines
1. Ensure all local tests pass before opening a Pull Request.
2. Link the PR to the relevant task or requirement ID.
3. In the PR description, summarize:
   - What changed
   - How to test / preview
   - Affected modules
4. Require at least one peer review from a related domain owner before merging to `develop`.
5. Squash and merge or rebase cleanly to maintain a readable git history.
