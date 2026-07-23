# Low-Level Designs

Created when an HLD reveals complexity requiring component-level detail before implementation.

## When to Create an LLD

- HLD component has non-trivial implementation complexity (e.g., custom auth flow, multi-step data pipeline)
- Implementation team needs precise API contracts, data schemas, or sequence diagrams
- Security review requires detailed auth flow documentation

## Naming Convention

`LLD-<service>-<component>.md`

Examples: `LLD-cloud-run-auth-flow.md`, `LLD-bigquery-partition-strategy.md`

## Template

```markdown
# LLD: <Component Name>
Date: YYYY-MM-DD
Author: gcp-architect
Parent HLD: architecture/HLD/<parent>.md

## Scope
<Which part of the HLD this LLD covers>

## Component Detail
<API contracts, data schemas, sequence diagrams>

## Implementation Notes
<Non-obvious constraints or tradeoffs the implementer must know>

## Test Plan
<How to verify this component works correctly>
```
