# FAAST Repository Sync

implementation for synchronizing FAAST skill Markdown files from the GitHub repository to the GitLab FAAST repository.

## Scope

The solution synchronizes only:


content/skills/**/*.md
```

It preserves the complete directory structure below `content/skills`.

The solution does not synchronize dashboards, workflows, branches, releases, issues, pull requests, team implementation files, or non-Markdown files.

## Architecture

```text
German GitHub FAAST repository
             |
             | Read latest source branch
             v
GitLab scheduled CI/CD pipeline
             |
             | Synchronize content/skills/**/*.md
             | Validate result and generate report
             v
Chinese GitLab FAAST repository
             |
             | Commit and push only if files changed
             v
Updated FAAST skills
```

## Repository contents

```text
.
├── .gitlab-ci.yml
├── config/
│   └── sync-config.example.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── HANDOVER.md
│   ├── OPERATIONS.md
├── scripts/
│   └── sync_skills.py
└── tests/
    └── test_sync_skills.py
```

## Prerequisites

- A GitLab Runner with access to the source GitHub repository and target GitLab repository
- A GitHub token or deploy key with read-only access to the source repository
- A GitLab project access token with `write_repository` access to the target repository


## Required GitLab CI/CD variables

**Settings > CI/CD > Variables** 

| Variable | Purpose | Recommended protection |
|---|---|---|
| `SOURCE_REPOSITORY_URL` | HTTPS clone URL of the German GitHub FAAST repository | Visible or masked |
| `SOURCE_BRANCH` | Visible |
| `SOURCE_GITHUB_TOKEN` | Read-only token for a private GitHub repository | Masked and protected |
| `TARGET_REPOSITORY_URL` | HTTPS clone URL of the Chinese GitLab FAAST repository | Visible or masked|
| `TARGET_BRANCH` | Target branch | Visible |
| `TARGET_GITLAB_TOKEN` | Project access token with `write_repository` | Masked and protected |
| `GIT_AUTHOR_NAME` | Commit author | Visible |
| `GIT_AUTHOR_EMAIL` | Technical commit email | Visible |

## Local validation

The synchronization logic can be tested without credentials:

```bash
python -m unittest discover -s tests -v
```

Run a dry run against two existing local repository folders:

```bash
python scripts/sync_skills.py \
  --source-repo ./source-repository \
  --target-repo ./target-repository \
  --dry-run
```

Run the actual file synchronization:

```bash
python scripts/sync_skills.py \
  --source-repo ./source-repository \
  --target-repo ./target-repository \
  --delete
```
```
Source
content/skills/<domain>/**/*.md

Target
docs/<domain>/**/*.md
````

`--delete` removes target Markdown files within the configured target skills folder when they no longer exist in the source. It does not delete non-Markdown files.

## GitLab schedule

After the pipeline has been validated manually, create a monthly pipeline schedule in the GitLab user interface. A suggested cron pattern is:

```text
0 2 1 * *
```

The actual execution time depends on the timezone configured for the GitLab schedule. The schedule should target the sync repository's default branch.

## First production run

1. Review and adapt `.gitlab-ci.yml`.
2. Configure all required CI/CD variables.
3. Protect the default branch and credentials according to local standards.
4. Run the pipeline manually with `DRY_RUN=true`.
5. Review the `sync-report.json` artifact.
6. Run the pipeline manually with `DRY_RUN=false`.
7. Verify the generated commit in the target GitLab repository.
8. Create and enable the monthly schedule.

See `docs/HANDOVER.md` for the complete handover checklist.
