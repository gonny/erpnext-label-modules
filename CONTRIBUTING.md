# Contributing

Thank you for contributing to **Label Calculator**!

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, released code. Protected — no direct push. |
| `develop` | Integration branch for completed features. |
| `feature/issue-{n}-short-desc` | Feature work tied to a GitHub issue. |
| `fix/issue-{n}-short-desc` | Bug fixes tied to a GitHub issue. |
| `chore/issue-{n}-short-desc` | Infrastructure / tooling changes. |

**Always branch from `develop`**, not `main`.

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional-scope>): <short summary>
```

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Add or update tests |
| `docs` | Documentation only |
| `chore` | Tooling, CI, deps, config |
| `refactor` | Code change that neither fixes a bug nor adds a feature |

Example: `feat(core): add material price lookup to calculator`

## Pull Request Checklist

Before opening a PR:

- [ ] Branch is based on `develop` (not `main`)
- [ ] `ruff check .` passes (zero warnings)
- [ ] `ruff format --check .` passes
- [ ] `mypy label_calculator/` passes
- [ ] `pytest -m unit` passes
- [ ] New code has unit tests (`@pytest.mark.unit` in `core/`)
- [ ] New DocType code has integration tests
- [ ] No secrets committed — `pre-commit run --all-files` passes
- [ ] PR description explains **what** and **why**
- [ ] PR is linked to its GitHub issue (`Closes #N`)

## Branch Protection Rules

The following rules are enforced on `main` and `develop`:

1. **Require pull request** — no direct push allowed.
2. **Require all CI checks to pass** — all GitHub Actions jobs must be green.
3. **Require at least 1 reviewer approval** before merge.
4. **Dismiss stale reviews** when new commits are pushed.

## Running the Full Validation Suite Locally

```bash
# Inside devcontainer or with Frappe installed

# 1. Lint
ruff check apps/label_calculator/ && ruff format --check apps/label_calculator/

# 2. Type check
mypy apps/label_calculator/label_calculator/

# 3. Unit tests (no Frappe needed)
cd apps/label_calculator && pytest -m unit

# 4. Integration tests (requires running bench)
cd /workspace/frappe-bench && bench run-tests --app label_calculator

# 5. All pre-commit hooks
pre-commit run --all-files
```
