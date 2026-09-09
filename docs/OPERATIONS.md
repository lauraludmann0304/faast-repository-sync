# Operations

## Normal operation

A scheduled pipeline runs monthly. A successful execution has one of two outcomes:

- No relevant changes: the job succeeds without a commit.
- Relevant changes: the job creates one commit in the configured target branch.

## Monitoring

The GitLab project owner should monitor:

- Scheduled pipeline status
- Failed jobs
- Token expiration
- Runner availability
- Push rejection caused by branch protection or concurrent target changes
- Unexpectedly high numbers of deleted or changed files in `sync-report.json`

## Recovery

If a synchronization commit is incorrect:

1. Disable the pipeline schedule.
2. Review the pipeline report and source commit in the generated commit message.
3. Revert the synchronization commit using the normal GitLab review process.
4. Correct the configuration or source content.
5. Perform a manual dry run.
6. Re-enable production synchronization after review.

## Manual dry run

Start a manual pipeline with:

```text
DRY_RUN=true
```

The job generates `sync-report.json` but does not commit or push target changes.

## Deletion policy

With `DELETE_REMOVED_MARKDOWN=true`, target Markdown files inside the target skills path are removed when missing in the source. Non-Markdown files remain untouched. Set the variable to `false` if deletions require separate approval.