---
name: vertex-ai
description: "Build and deploy ML models and generative AI applications on Vertex AI. Covers Model Garden, Gemini API, custom training, endpoint deployment, Agent Builder, and IAM. Warns before deploying endpoints (billable). Integrates with Vertex AI MCP server."
version: "0.1"
triggers:
  - "vertex AI"
  - "Gemini on GCP"
  - "model garden"
  - "deploy ML model"
  - "vertex endpoint"
  - "generative AI GCP"
  - "agent builder"
  - "vertex training"
  - "PaLM"
  - "Gemini API"
  - "vertex AI pipeline"
required_scopes:
  - aiplatform.endpoints.create
  - aiplatform.endpoints.get
  - aiplatform.endpoints.predict
  - aiplatform.models.get
  - aiplatform.models.list
  - aiplatform.trainingPipelines.create
  - aiplatform.trainingPipelines.get
mcp_servers:
  - google-vertex-ai
---

# Vertex AI

Unified ML platform for training, deploying, and serving models — including Gemini, generative AI, and custom models.

## Key Products

| Product | Use |
|---------|-----|
| Gemini API on Vertex | Production-grade Gemini access with data governance |
| Model Garden | Browse and deploy 150+ models (Gemini, Llama, etc.) |
| Custom Training | Train on managed infrastructure (GPUs/TPUs) |
| Vertex AI Endpoints | Serve predictions from deployed models |
| Agent Builder | Build conversational agents on Vertex |
| Vertex AI Pipelines | Orchestrate ML workflows (Kubeflow Pipelines) |

## Core Patterns

### Call Gemini via Vertex (Python)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="PROJECT_ID", location="us-central1")
model = GenerativeModel("gemini-2.0-flash-001")
response = model.generate_content("Explain Cloud Run in one sentence.")
print(response.text)
```

### Deploy an endpoint (billable — confirm first)

```bash
# Billable: endpoints charge per node-hour when deployed
gcloud ai endpoints create \
  --display-name=ENDPOINT_NAME \
  --region=REGION \
  --project=PROJECT_ID
```

### Grant Vertex AI access (least-privilege)

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Safety Rules

- Endpoints incur cost even when idle — undeploy when not needed
- Use `roles/aiplatform.user` for inference; `roles/aiplatform.admin` only for platform admins
- Cost warning: GPUs and TPUs are expensive — confirm instance type and count before training

## References

- [Vertex AI Overview](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform)
- [Generative AI on Vertex](https://cloud.google.com/vertex-ai/generative-ai/docs/overview)
- [Vertex AI IAM](https://cloud.google.com/vertex-ai/docs/general/access-control)
- [Model Garden](https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models)
