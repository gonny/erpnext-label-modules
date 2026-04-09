---
description: Describe when these instructions should be loaded by the agent based on task context
# applyTo: 'Describe when these instructions should be loaded by the agent based on task context' # when provided, instructions will automatically be added to the request context when the pattern matches an attached file
---

<!-- Tip: Use /create-instructions in chat to generate content with agent assistance -->

## 1. Available MCP Tools Reference

| Tool | What It Does | When to Use |
|---|---|---|
| `github` | Manage issues, PRs, branches | Creating PRs, reading issue details |
| `filesystem` | Read/write files in workspace | Navigating codebase, reading configs, reading Frappe source |
| `shell` | Execute allowed commands | Running tests, linting, bench commands, DB queries via `bench console` / `bench mariadb` |
| `context7` | Library documentation | Fetching current API docs for Frappe Framework and Python libs |

## Documentation
- Documentation is in `docs/` directory.