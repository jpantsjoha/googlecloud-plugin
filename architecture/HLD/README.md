# High-Level Designs

One HLD per feature or use case. Created by `gcp-architect` (for GCP scope) or `solution-designer` (for multi-vendor scope).

## When to Create an HLD

- Any feature or change touching ≥2 GCP services
- Any new service integration or cross-vendor component
- Any infrastructure change with cost or security implications
- Required by the GCP Design Gate before implementation begins

## Naming Convention

`HLD-<short-description>.md`

Examples: `HLD-cloud-run-to-bigquery-pipeline.md`, `HLD-multi-cloud-auth.md`

## Template

```markdown
# HLD: <Feature / Solution Name>
Date: YYYY-MM-DD
Author: gcp-architect | solution-designer
Status: draft | review | approved

## Problem
<What is being solved — 2-3 sentences>

## Constraints
<Compliance, latency, cost ceiling, existing contracts, team skills>

## Architecture
<Component diagram or description>

## GCP Services Involved
| Service | Purpose | IAM Scopes |
|---------|---------|-----------|
| ...     | ...     | ...       |

## Integration Points
<Cross-service or cross-vendor data flows>

## IAM Design
<Service accounts, roles, least-privilege rationale>

## Network Design
<VPC, subnets, firewall, private connectivity>

## Well-Architected Alignment
| Pillar | How addressed |
|--------|--------------|
| Security | ... |
| Reliability | ... |
| Cost | ... |

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| ... | ... | ... | ... |

## ADRs
<Links to supporting ADRs>

## Acceptance Criteria
- [ ] ...
```
