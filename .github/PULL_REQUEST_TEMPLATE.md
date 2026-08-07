## What and why

<!-- The diff shows what changed. Explain why it needed to. -->

## Gate

- [ ] `make gate` passes locally

<!-- If `make lint` returned HTTP 429 you were rate-limited by cloud.google.com,
     not broken. Say so here and let CI arbitrate. -->

## If this touches skills

- [ ] Frontmatter uses only the closed Agent Skills field set — plugin-specific
      keys are namespaced under `metadata` as string values
- [ ] Every trigger in `metadata` also appears in `description`
- [ ] Where scope overlaps another skill, both descriptions name each other and
      draw the boundary
- [ ] Every technical claim cites a live Google Cloud doc

## Safety

- [ ] No credential values — locations only
- [ ] No `roles/owner` or `roles/editor` in examples
- [ ] Billable or destructive commands carry a warning
- [ ] No public buckets or unauthenticated endpoints without stated intent

## Records

- [ ] `CHANGELOG.md` updated if user-facing
- [ ] ADR added for a significant decision
- [ ] `research/coverage-matrix.md` updated if a skill's status changed
