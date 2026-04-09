---
description: When you complete work on your task, please follow these steps to ensure quality and consistency in the project.
applyTo: '**' # when provided, instructions will automatically be added to the request context when the pattern matches an attached file
---

## Update ERD Model
- If you have made changes to the database schema, please update the ERD model accordingly.
- ERD models are located in the `docs/ERD.md` file. 

## Update Backlog
- If your task is related to a user story or feature, please update the backlog.
- Backlog items are located in the `docs/Backlog.md` file.
- If anything left from your tasks, please add it to the backlog with a clear description and priority.

## Code review
You review code that was just written or changed. Your job is to make it production-ready.

### What You Do

1. **Read** the changed files and understand what was implemented
2. **Scout** — Use Codebase Scout to find duplicates and similar patterns in the codebase
3. **Simplify** — Make code shorter, clearer, more idiomatic. Refactor if needed.
4. **Document** — Add PyDoc/TSDoc where intent isn't obvious. Don't over-document.
5. **Deduplicate** — If Scout found similar code, consolidate.
6. **Verify** — Run ALL relevant quality gates and report results:
   - Tests pass?
   - Types check?
   - Linter clean?
   - Build succeeds?
   - Documented with PyDoc/TSDoc where needed?

## Pass Quality Gates
- All tests must pass.
- Code must be properly tested with good coverage.
  



