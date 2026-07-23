.PHONY: all gate validate manifest preflight lint mermaid test check crawl crawl-dry hooks help

PYTHON  := python3
SCRIPTS := scripts
TESTS   := tests/skill-smoke-tests

# ─── 3-minute validation gate (validate + manifest + lint + test) ───────────
# This is the pre-commit gate. Install the hook once with: make hooks

gate: validate manifest mermaid lint test
	@echo ""
	@echo "Gate passed: validate + manifest + mermaid + lint + test"

# ─── Individual targets ──────────────────────────────────────────────────────

validate:
	@echo "==> Validating SKILL.md contracts..."
	@$(PYTHON) $(SCRIPTS)/validate_skills.py

manifest:
	@echo "==> Validating plugin packaging (Claude · Antigravity · Codex · Kimi)..."
	@$(PYTHON) $(SCRIPTS)/validate_plugin.py

preflight:
	@echo "==> Preflight: infer GCP context from environment (read-only)..."
	@$(PYTHON) $(SCRIPTS)/preflight.py

mermaid:
	@echo "==> Linting Mermaid diagrams (GitHub render-safety)..."
	@$(PYTHON) $(SCRIPTS)/validate_mermaid.py

lint:
	@echo "==> Checking reference URLs..."
	@$(PYTHON) $(SCRIPTS)/check_links.py

test:
	@echo "==> Running skill smoke tests..."
	@$(PYTHON) -m pytest $(TESTS)/ -v --tb=short -q

check:
	@echo "==> Running freshness check (hash drift detection)..."
	@$(PYTHON) $(SCRIPTS)/freshness_check.py

# ─── Research pipeline ───────────────────────────────────────────────────────

crawl:
	@echo "==> Crawling GCP documentation sources (all services)..."
	@$(PYTHON) $(SCRIPTS)/research_crawl.py

crawl-dry:
	@echo "==> Dry-run crawl (fetch only, no files written)..."
	@$(PYTHON) $(SCRIPTS)/research_crawl.py --dry-run

crawl-list:
	@$(PYTHON) $(SCRIPTS)/research_crawl.py --list

# ─── Git hooks ───────────────────────────────────────────────────────────────

hooks:
	@git config core.hooksPath .githooks
	@echo "Pre-commit hook active: 'make gate' runs on every commit (.githooks/pre-commit)"

# ─── Help ────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "GoogleCloud Plugin — Makefile Targets"
	@echo ""
	@echo "  make gate        Pre-commit gate: validate + manifest + mermaid + lint + test"
	@echo "  make validate    Validate all SKILL.md frontmatter (contract check)"
	@echo "  make manifest    Validate plugin is installable (Claude/AGY/Codex/Kimi)"
	@echo "  make mermaid     Lint Mermaid diagrams for GitHub render-safety"
	@echo "  make lint        Check all reference URLs resolve (HTTP 200)"
	@echo "  make test        Run skill smoke tests via pytest"
	@echo "  make check       Freshness check: hash drift detection vs live sources"
	@echo "  make hooks       Install the pre-commit hook (runs make gate)"
	@echo ""
	@echo "  make crawl       Crawl all GCP doc sources, write research/raw/"
	@echo "  make crawl-dry   Crawl without writing files (preview)"
	@echo "  make crawl-list  List all crawlable services"
	@echo ""
