#!/usr/bin/env python3
"""Fetch GCP documentation sources and save raw notes + metadata.

Populates research/raw/<service>.md and updates research/SOURCES.md
with URL, retrieval date, and content hash for every source.

Exit 0: crawl complete (even with partial fetch failures — listed in output).
Exit 1: unexpected error or unknown --service argument.
"""
import sys
import hashlib
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "research" / "raw"
SOURCES_FILE = ROOT / "research" / "SOURCES.md"
TIMEOUT = 20
HEADERS = {"User-Agent": "googlecloud-plugin/0.1 research-crawler"}

# Canonical source list — extend here as new services are added.
# Format: service_key -> list of (title, url) tuples.
SOURCES: dict[str, list[tuple[str, str]]] = {
    "cloud-run": [
        ("Cloud Run Overview", "https://cloud.google.com/run/docs/overview/what-is-cloud-run"),
        ("Cloud Run Quickstart", "https://cloud.google.com/run/docs/quickstarts"),
        ("Cloud Run IAM", "https://cloud.google.com/run/docs/securing/managing-access"),
        ("Cloud Run Pricing", "https://cloud.google.com/run/pricing"),
        ("Cloud Run gcloud reference", "https://cloud.google.com/sdk/gcloud/reference/run"),
    ],
    "gke": [
        ("GKE Overview", "https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview"),
        ("GKE Autopilot Overview", "https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview"),
        ("GKE Security Overview", "https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview"),
        ("GKE Networking Overview", "https://cloud.google.com/kubernetes-engine/docs/concepts/network-overview"),
        ("Workload Identity Federation", "https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity"),
    ],
    "iam": [
        ("IAM Overview", "https://cloud.google.com/iam/docs/overview"),
        ("IAM Best Practices", "https://cloud.google.com/iam/docs/using-iam-securely"),
        ("Service Account Overview", "https://cloud.google.com/iam/docs/service-account-overview"),
        ("IAM Conditions", "https://cloud.google.com/iam/docs/conditions-overview"),
        ("Predefined Roles Reference", "https://cloud.google.com/iam/docs/understanding-roles"),
    ],
    "bigquery": [
        ("BigQuery Introduction", "https://cloud.google.com/bigquery/docs/introduction"),
        ("BigQuery Access Control", "https://cloud.google.com/bigquery/docs/access-control"),
        ("BigQuery Pricing", "https://cloud.google.com/bigquery/pricing"),
        ("BigQuery Performance Best Practices", "https://cloud.google.com/bigquery/docs/best-practices-performance-overview"),
        ("BigQuery Storage Overview", "https://cloud.google.com/bigquery/docs/storage-overview"),
    ],
    "cloud-storage": [
        ("Cloud Storage Overview", "https://cloud.google.com/storage/docs/introduction"),
        ("Cloud Storage IAM", "https://cloud.google.com/storage/docs/access-control/iam"),
        ("Cloud Storage Best Practices", "https://cloud.google.com/storage/docs/best-practices"),
        ("Cloud Storage Pricing", "https://cloud.google.com/storage/pricing"),
        ("Object Lifecycle Management", "https://cloud.google.com/storage/docs/lifecycle"),
    ],
    "vertex-ai": [
        ("Vertex AI Overview", "https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform"),
        ("Vertex AI Generative AI", "https://cloud.google.com/vertex-ai/generative-ai/docs/overview"),
        ("Vertex AI IAM", "https://cloud.google.com/vertex-ai/docs/general/access-control"),
        ("Vertex AI Pricing", "https://cloud.google.com/vertex-ai/pricing"),
        ("Vertex AI Model Garden", "https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models"),
        ("Agent Builder Overview", "https://cloud.google.com/dialogflow/cx/docs/concept/agent"),
    ],
    "networking": [
        ("VPC Overview", "https://cloud.google.com/vpc/docs/vpc"),
        ("VPC Firewall Rules", "https://cloud.google.com/vpc/docs/firewalls"),
        ("Cloud Load Balancing Overview", "https://cloud.google.com/load-balancing/docs/load-balancing-overview"),
        ("Cloud Armor Overview", "https://cloud.google.com/armor/docs/cloud-armor-overview"),
        ("Private Google Access", "https://cloud.google.com/vpc/docs/private-google-access"),
        ("Shared VPC Overview", "https://cloud.google.com/vpc/docs/shared-vpc"),
    ],
    "logging-monitoring": [
        ("Cloud Logging Overview", "https://cloud.google.com/logging/docs/overview"),
        ("Cloud Monitoring Overview", "https://cloud.google.com/monitoring/docs/monitoring-overview"),
        ("Cloud Trace Overview", "https://cloud.google.com/trace/docs/overview"),
        ("Cloud Profiler Overview", "https://cloud.google.com/profiler/docs/about-profiler"),
        ("Error Reporting Overview", "https://cloud.google.com/error-reporting/docs/overview"),
        ("Log-based Metrics", "https://cloud.google.com/logging/docs/logs-based-metrics"),
    ],
    "mcp-servers": [
        ("MCP Toolbox for Databases", "https://googleapis.github.io/genai-toolbox/"),
        ("GenAI Toolbox GitHub", "https://github.com/googleapis/genai-toolbox"),
        ("Google MCP Servers Repository", "https://github.com/googleapis/mcp-toolbox-for-databases"),
        ("Model Context Protocol Spec", "https://modelcontextprotocol.io/introduction"),
    ],
    "well-architected": [
        ("Google Cloud Architecture Framework", "https://cloud.google.com/architecture/framework"),
        ("Operational Excellence Pillar", "https://cloud.google.com/architecture/framework/operational-excellence"),
        ("Security Pillar", "https://cloud.google.com/architecture/framework/security"),
        ("Reliability Pillar", "https://cloud.google.com/architecture/framework/reliability"),
        ("Cost Optimization Pillar", "https://cloud.google.com/architecture/framework/cost-optimization"),
        ("Performance Pillar", "https://cloud.google.com/architecture/framework/performance"),
    ],
    "terraform-gcp": [
        ("Cloud Foundation Toolkit", "https://cloud.google.com/foundation-toolkit"),
        ("Terraform Google Provider Docs", "https://registry.terraform.io/providers/hashicorp/google/latest/docs"),
        ("CFT GitHub Organization", "https://github.com/GoogleCloudPlatform/cloud-foundation-toolkit"),
        ("terraform-google-modules", "https://github.com/terraform-google-modules"),
        ("GCP Landing Zone Blueprint", "https://cloud.google.com/architecture/security-foundations"),
    ],
    "solution-designer": [
        ("Google Cloud Architecture Center", "https://cloud.google.com/architecture"),
        ("Multi-cloud Architecture Patterns", "https://cloud.google.com/architecture/hybrid-and-multi-cloud-architecture-patterns"),
        ("Google Cloud Decision Trees", "https://cloud.google.com/architecture/framework"),
    ],
    "gcp-architect": [
        ("GCP Architecture Framework", "https://cloud.google.com/architecture/framework"),
        ("GCP Reference Architectures", "https://cloud.google.com/architecture"),
        ("Cloud Foundation Toolkit Blueprints", "https://cloud.google.com/foundation-toolkit"),
    ],
    "gcp-security": [
        ("GCP Security Best Practices", "https://cloud.google.com/security/best-practices"),
        ("Security Foundations Blueprint", "https://cloud.google.com/architecture/security-foundations"),
        ("GCP Well-Architected Security", "https://cloud.google.com/architecture/framework/security"),
        ("CIS GCP Benchmark", "https://cloud.google.com/security/compliance/cis-benchmarks"),
    ],
    "gcp-ops": [
        ("SRE Book — Google", "https://sre.google/sre-book/table-of-contents/"),
        ("Cloud Monitoring Overview", "https://cloud.google.com/monitoring/docs/monitoring-overview"),
        ("Cloud Operations Suite", "https://cloud.google.com/products/operations"),
        ("GCP Incident Management", "https://cloud.google.com/architecture/incident-management"),
    ],
    "gcp-qa": [
        ("Cloud Build Overview", "https://cloud.google.com/build/docs/overview"),
        ("GCP Testing Best Practices", "https://cloud.google.com/architecture/framework/operational-excellence"),
        ("Artifact Registry Overview", "https://cloud.google.com/artifact-registry/docs/overview"),
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(url: str) -> tuple[bytes, str]:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read(), "OK"
    except urllib.error.HTTPError as e:
        return b"", f"HTTP {e.code}"
    except Exception as e:
        return b"", f"{type(e).__name__}: {e}"


def crawl_service(
    service: str, entries: list[tuple[str, str]], dry_run: bool
) -> list[dict]:
    results: list[dict] = []
    print(f"\n[{service}] — {len(entries)} source(s)")

    lines = [
        f"# {service} — Research Notes",
        f"Retrieved: {now_iso()}",
        "",
    ]

    for title, url in entries:
        content, status = fetch(url)
        h = hashlib.sha256(content).hexdigest() if content else ""
        mark = "OK  " if status == "OK" else "FAIL"
        print(f"  {mark}  {title}")
        if status != "OK":
            print(f"        {url}")
            print(f"        Error: {status}")

        results.append(
            {
                "service": service,
                "title": title,
                "url": url,
                "status": status,
                "hash": h,
                "retrieved": now_iso(),
                "size_bytes": len(content),
            }
        )

        lines += [
            f"## {title}",
            f"- **URL**: {url}",
            f"- **Retrieved**: {now_iso()}",
            f"- **Hash**: {h}",
            f"- **Status**: {status}",
            f"- **Size**: {len(content):,} bytes",
            "",
        ]

    if not dry_run:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        out = RAW_DIR / f"{service}.md"
        out.write_text("\n".join(lines))
        print(f"  Saved → {out}")

    return results


def write_sources(all_results: list[dict]) -> None:
    by_service: dict[str, list[dict]] = {}
    for r in all_results:
        by_service.setdefault(r["service"], []).append(r)

    lines = [
        "# Research Sources",
        f"Last updated: {now_iso()}",
        "",
        "Every source URL is stored with retrieval date and content hash for audit.",
        "",
    ]

    for service, entries in sorted(by_service.items()):
        lines.append(f"## {service}")
        for e in entries:
            lines += [
                f"### {e['title']}",
                f"- **URL**: {e['url']}",
                f"- **Retrieved**: {e['retrieved']}",
                f"- **Hash**: {e['hash']}",
                f"- **Status**: {e['status']}",
                "",
            ]

    SOURCES_FILE.write_text("\n".join(lines))
    print(f"\nSources index → {SOURCES_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl GCP documentation sources")
    parser.add_argument("--service", help="Crawl a single service only")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't write files")
    parser.add_argument("--list", action="store_true", help="List services and exit")
    args = parser.parse_args()

    if args.list:
        for s in sorted(SOURCES):
            print(f"  {s}  ({len(SOURCES[s])} sources)")
        return

    if args.service:
        if args.service not in SOURCES:
            print(f"Unknown service '{args.service}'. Use --list.", file=sys.stderr)
            sys.exit(1)
        targets = {args.service: SOURCES[args.service]}
    else:
        targets = SOURCES

    all_results: list[dict] = []
    for service, entries in targets.items():
        all_results.extend(crawl_service(service, entries, dry_run=args.dry_run))

    if not args.dry_run:
        write_sources(all_results)

    failures = [r for r in all_results if r["status"] != "OK"]
    total = len(all_results)
    print(f"\nCrawl complete: {total - len(failures)}/{total} OK, {len(failures)} failed")


if __name__ == "__main__":
    main()
