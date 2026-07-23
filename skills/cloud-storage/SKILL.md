---
name: cloud-storage
description: "Manage object storage on Google Cloud Storage. Covers bucket creation, IAM, uniform access control, lifecycle policies, signed URLs, and gsutil/gcloud CLI patterns. Enforces private-by-default: never creates public buckets without explicit intent and gcp-security sign-off."
version: "0.1"
triggers:
  - "cloud storage"
  - "GCS"
  - "bucket"
  - "gsutil"
  - "object storage"
  - "upload to GCP"
  - "storage IAM"
  - "signed URL"
  - "lifecycle policy"
  - "storage class"
required_scopes:
  - storage.buckets.create
  - storage.buckets.get
  - storage.buckets.getIamPolicy
  - storage.buckets.setIamPolicy
  - storage.objects.create
  - storage.objects.get
  - storage.objects.list
mcp_servers:
  - google-storage
---

# Cloud Storage

Highly durable, globally consistent object storage. Private by default — always review IAM before making anything public.

## Safety Rule — Never Public by Default

New buckets must use uniform bucket-level access and must not grant `allUsers` or `allAuthenticatedUsers` without explicit design intent and gcp-security sign-off.

## Core Patterns

### Create a bucket (private, uniform access)

```bash
gcloud storage buckets create gs://BUCKET_NAME \
  --location=REGION \
  --uniform-bucket-level-access \
  --project=PROJECT_ID
```

### Grant access (least-privilege)

```bash
gcloud storage buckets add-iam-policy-binding gs://BUCKET_NAME \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Upload / download

```bash
gcloud storage cp LOCAL_FILE gs://BUCKET_NAME/path/
gcloud storage cp gs://BUCKET_NAME/path/FILE ./local/
```

### Lifecycle policy (auto-delete after N days)

```bash
cat > /tmp/lifecycle.json <<'EOF'
{
  "rule": [{
    "action": {"type": "Delete"},
    "condition": {"age": 90}
  }]
}
EOF
gcloud storage buckets update gs://BUCKET_NAME \
  --lifecycle-file=/tmp/lifecycle.json
```

### Generate a signed URL (time-limited access)

```bash
gcloud storage sign-url gs://BUCKET_NAME/OBJECT \
  --duration=1h \
  --private-key-file=KEY_FILE
```

## References

- [Cloud Storage Overview](https://cloud.google.com/storage/docs/introduction)
- [Cloud Storage IAM](https://cloud.google.com/storage/docs/access-control/iam)
- [Best Practices](https://cloud.google.com/storage/docs/best-practices)
- [Object Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
