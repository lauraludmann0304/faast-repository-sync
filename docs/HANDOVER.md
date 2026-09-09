# Handover Guide

## Deliverable

This repository provides the synchronization script, GitLab CI/CD definition, automated tests, configuration example, architecture description, security guidance, and operational guidance.

## Information to be supplied by the receiving team

- GitLab Runner and network path
- Approved schedule timezone and execution time
- Token owner, expiry date, and rotation process

## Deployment checklist

- [ ] Create the read-only GitHub credential.
- [ ] Create the GitLab project access token with repository write access.
- [ ] Configure masked and protected CI/CD variables.
- [ ] Confirm Runner access to GitHub and GitLab.
- [ ] Review target branch protection.
- [ ] Run unit tests.
- [ ] Run a manual pipeline with `DRY_RUN=true`.
- [ ] Review `sync-report.json`.
- [ ] Run the first production synchronization manually.
- [ ] Review the target commit and folder structure.
- [ ] Create the monthly pipeline schedule.
- [ ] Assign operational ownership and failure notifications.
- [ ] Document token rotation and incident contacts.

## Acceptance criteria

- The pipeline copies all source `.md` files below the configured skills path.
- Relative directories and file names are preserved.
- New and modified Markdown files are reflected in the target.
- Removed source Markdown files are handled according to the deletion setting.
- Non-Markdown target files are not changed by the script.
- No commit is generated when the repositories are already synchronized.
- The report identifies copied, updated, deleted, and unchanged files.
- Credentials are not stored in the repository.
- A monthly GitLab pipeline schedule is configured and owned by the receiving team.
