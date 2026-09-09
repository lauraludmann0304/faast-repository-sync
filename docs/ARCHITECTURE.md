# Architecture

## Objective

Keep the Markdown-based FAAST skill catalogue in the Chinese GitLab repository aligned with the German GitHub source repository.

## Design decision

The automation is hosted in a dedicated GitLab sync repository and executed by a scheduled GitLab CI/CD pipeline. The pipeline reads the source repository, updates the target repository, and creates a traceable Git commit only when relevant files changed.

## Synchronization boundary

Included:

```text
content/skills/**/*.md
```

Excluded:

- Files outside the skills directory
- Non-Markdown files
- Git metadata and history from the source repository
- GitHub Actions and GitLab CI/CD configuration from the FAAST repositories
- Issues, pull requests, merge requests, releases, dashboards, and wiki content

# Mapping

Source:
content/skills/<domain>

Target:
docs/<domain>

Example:
content/skills/GDPR/GDPR-CREATE-001.md

docs/GDPR/GDPR-CREATE-001.md
``
## Processing sequence

1. Validate required environment variables.
2. Clone the configured source branch from GitHub.
3. Clone the configured target branch from GitLab.
4. Identify all source Markdown files below the configured source skills path.
5. Copy new or changed Markdown files while retaining their relative paths.
6. Optionally remove target Markdown files that disappeared from the source.
7. Leave all non-Markdown target files unchanged.
8. Generate a JSON synchronization report.
9. Commit and push only when the target working tree contains relevant changes.

## Idempotency

Running the pipeline multiple times for the same source state produces no additional target commit after the first successful synchronization.

## Failure behaviour

The job fails before pushing if cloning, validation, synchronization, testing, committing, or pushing fails. GitLab retains the synchronization report as a pipeline artifact when one was generated.

## Concurrency

The pipeline uses a GitLab `resource_group` so that only one synchronization job for this project runs at a time.
