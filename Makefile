.PHONY: all gate validate lint test check crawl crawl-dry help

PYTHON  := python3
SCRIPTS := scripts
TESTS   := tests/skill-smoke-tests

# ─── 3-minute validation gate (validate + lint + test) ──────────────────────

gate: validate lint test
	@echo ""
	@echo "Gate passed: validate + lint + test"

# ─── Individual targets ──────────────────────────────────────────────────────

validate:
	@echo "==> Validating SKILL.md contracts..."
	@$(PYTHON) $(SCRIPTS)/validate_skills.py

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

# ─── Help ────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "GoogleCloud Plugin — Makefile Targets"
	@echo ""
	@echo "  make gate        3-minute validation gate: validate + lint + test"
	@echo "  make validate    Validate all SKILL.md frontmatter (contract check)"
	@echo "  make lint        Check all reference URLs resolve (HTTP 200)"
	@echo "  make test        Run skill smoke tests via pytest"
	@echo "  make check       Freshness check: hash drift detection vs live sources"
	@echo ""
	@echo "  make crawl       Crawl all GCP doc sources, write research/raw/"
	@echo "  make crawl-dry   Crawl without writing files (preview)"
	@echo "  make crawl-list  List all crawlable services"
	@echo ""
