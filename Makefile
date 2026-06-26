APP_NAME ?= label_calculator
BENCH_DIR ?= frappe-bench
SITE ?=
PYTHON ?= python
PYTEST ?= $(PYTHON) -m pytest
BENCH := cd $(BENCH_DIR) && bench

.PHONY: help check-site unit-test integration-test bench-start bench-stop reinstall-app refresh-data fresh-start

help:
	@echo "Available targets:"
	@echo "  make unit-test            Run the fast pure-Python unit tests."
	@echo "  make integration-test     Run the bench-backed integration tests (requires SITE=<sitename>)."
	@echo "  make reinstall-app        Reinstall the app on the selected site (requires SITE=<sitename>)."
	@echo "  make refresh-data         Migrate the site and reinstall the app to refresh data (requires SITE=<sitename>)."
	@echo "  make fresh-start          Reinstall the site and app for a clean local start (requires SITE=<sitename>)."
	@echo "  make bench-start          Start the local Frappe bench."
	@echo "  make bench-stop           Stop the local Frappe bench."

check-site:
	@test -n "$(SITE)" || { echo "SITE must be set (example: make integration-test SITE=localhost)"; exit 1; }

unit-test:
	PYTHONPATH=$(CURDIR)/apps/$(APP_NAME) $(PYTEST) -m unit -q

integration-test: check-site
	$(BENCH) run-tests --app $(APP_NAME) --site $(SITE)

bench-start:
	$(BENCH) start

bench-stop:
	$(BENCH) stop || true

reinstall-app: check-site
	$(BENCH) --site $(SITE) uninstall-app $(APP_NAME) || true
	$(BENCH) --site $(SITE) install-app $(APP_NAME)

refresh-data: check-site
	$(BENCH) --site $(SITE) migrate
	$(MAKE) reinstall-app SITE=$(SITE)

fresh-start: check-site
	$(BENCH) --site $(SITE) reinstall --yes
	$(BENCH) --site $(SITE) install-app $(APP_NAME)
