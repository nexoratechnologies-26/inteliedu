# Workflow: Test Project

## Purpose
Standardized procedures for running automated tests across the frontend, backend, AI pipeline, and 3D graphics subsystems.

---

## 1. Directory Breakdown for Tests
All shared test suites and integration verification tests reside in `tests/`:
- `tests/frontend/`: UI component unit tests, render tests, and user event simulation.
- `tests/backend/`: Controller unit tests, route integration tests, and middleware tests.
- `tests/ai/`: RAG retrieval precision checks, prompt output schema validators, embedding dimension tests.
- `tests/threejs/`: 3D loader checks, scene assembly tests, canvas resize and WebGL memory lifecycle tests.

---

## 2. Running Test Suites

### Root Level Command
```bash
npm run test           # Run all unit and integration test suites
```

### Module Level Commands
- **Frontend**:
  ```bash
  npm run test:frontend
  ```
- **Backend**:
  ```bash
  npm run test:backend
  ```
- **AI Pipelines**:
  ```bash
  npm run test:ai
  ```
- **3D Graphics**:
  ```bash
  npm run test:threejs
  ```

---

## 3. Test Requirements & Pass Criteria
- **Coverage**: Critical authentication, authorization, and data mutation paths must have unit test coverage.
- **Mocking**: External third-party API calls (Gemini LLM API, Supabase remote instances, WebRTC peers) must use mocks/stubs during automated test execution.
- **Fail Fast**: Any failing test blocks PR merge to `develop` or `main`.
