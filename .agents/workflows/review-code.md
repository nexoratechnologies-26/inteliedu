# Workflow: Review Code

## Purpose
Ensure consistent quality, security, domain ownership adherence, and maintainability across all pull requests before merging.

---

## 1. Review Checklist for Reviewers

### A. Ownership & Boundaries
- [ ] Did the author modify files only within their assigned domain?
- [ ] If cross-domain files were changed, is there explicit justification or prior sign-off from that domain owner?
- [ ] Are API endpoints and contracts documented and adhered to?

### B. Security & Secrets
- [ ] Are there zero hardcoded API keys, database passwords, or JWT secrets?
- [ ] Are all new environment variables documented in `.env.example`?
- [ ] Is input sanitized and validated before processing?
- [ ] Are Supabase RLS policies maintained for new database tables?

### C. Code Quality & Standards
- [ ] Does the code adhere to `coding-standards.md`?
- [ ] Are variable and function names descriptive and idiomatic?
- [ ] Are error handlers implemented gracefully?
- [ ] Are 3D assets cleaned up and memory disposed of properly?

### D. Testing & Documentation
- [ ] Are new features accompanied by relevant tests in `tests/`?
- [ ] Did all automated CI test suites pass?
- [ ] Are API routes documented in `docs/api-documentation.md` if modified?

---

## 2. Review Resolution & Approval
- At least **one approving review** from a relevant domain peer is required.
- Address all inline comments before requesting re-review.
- Merge using squash-and-merge or clean rebase according to `git-workflow.md`.
