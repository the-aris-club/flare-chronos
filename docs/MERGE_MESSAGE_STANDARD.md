# Merge Message Standard

Use this format for every merge commit and squash commit.

## Format

```
<type>(<scope>): <short summary>

<body>

<footer>
```

## Type

- `feat` — new capability
- `fix` — bug or security fix
- `refactor` — no behavior change
- `docs` — documentation only
- `ci` — CI/CD change
- `chore` — maintenance

## Scope

Short noun for the affected area: `api`, `workbench`, `core`, `ingestion`, `ci`, `docs`, `security`.

## Short summary

- Imperative mood ("add", "fix", "remove"), max 72 characters.
- No trailing period.

## Body

- Explain what changed and why. One paragraph or bullet list.
- Reference the issue or PR number.

## Footer

- `Closes #123` for issues closed by the merge.
- `BREAKING CHANGE: ...` if the change is not backward compatible.

## Examples

```
fix(security): resolve security audit findings

Addresses 9 confirmed findings: shell injection in CD, unbounded
request inputs, run-id oracle, path traversal, unpinned actions,
runtime data in image, FIRMS key leak, public ports, PDF raw HTML.

Closes #30
```

```
feat(api): add per-user rate limit on analysis stream

Limits each principal to 10 concurrent runs to protect model spend.

Closes #42
```