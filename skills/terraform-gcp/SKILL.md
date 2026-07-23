---
name: terraform-gcp
description: "Terraform patterns for Google Cloud using the official google and google-beta providers and Cloud Foundation Toolkit modules. Covers project structure, state management, IAM, and CFT blueprint usage. Warns before terraform apply (billable and potentially destructive)."
version: "0.1"
triggers:
  - "terraform GCP"
  - "terraform google"
  - "IaC GCP"
  - "cloud foundation toolkit"
  - "CFT"
  - "terraform plan GCP"
  - "terraform apply GCP"
  - "GCP modules"
  - "landing zone terraform"
  - "terraform google provider"
required_scopes:
  - resourcemanager.projects.get
  - resourcemanager.projects.setIamPolicy
  - serviceusage.services.enable
mcp_servers: []
---

# Terraform — GCP

Infrastructure as Code for Google Cloud using the official Terraform provider and Cloud Foundation Toolkit (CFT).

## Safety Rule — Plan Before Apply

```bash
# Always plan first
terraform plan -out=tfplan

# Review the plan — look for unexpected destroys
# Only apply after confirming no unexpected changes
terraform apply tfplan
```

## Provider Setup

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  backend "gcs" {
    bucket = "PROJECT_ID-tfstate"
    prefix = "env/prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

## CFT Module Usage (recommended over writing from scratch)

```hcl
# Example: GKE cluster via CFT module
module "gke" {
  source  = "terraform-google-modules/kubernetes-engine/google//modules/autopilot-cluster"
  version = "~> 33.0"

  project_id = var.project_id
  name       = "my-cluster"
  region     = var.region
  network    = module.vpc.network_name
  subnetwork = module.vpc.subnets_names[0]
}
```

## State Management

- State in GCS bucket (not local, not git)
- One state file per environment (`env/dev`, `env/staging`, `env/prod`)
- Bucket versioning enabled for state rollback
- State lock via GCS object versioning (built in to google backend)

## Module Structure (project convention)

```
infra/
├── modules/           # Reusable modules
│   └── service/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf    # Calls modules
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       └── terraform.tfvars
└── backend.tf
```

## References

- [Cloud Foundation Toolkit](https://cloud.google.com/foundation-toolkit)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [CFT GitHub](https://github.com/GoogleCloudPlatform/cloud-foundation-toolkit)
- [terraform-google-modules](https://github.com/terraform-google-modules)
- [GCP Security Foundations Blueprint](https://cloud.google.com/architecture/security-foundations)
