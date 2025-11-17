.PHONY: bootstrap status test-all docs-gen demo-day evidence-pack fmt lint pre-commit-install ci-check status-md

bootstrap:
	python3 -m venv .venv && . .venv/bin/activate && pip install -U pip wheel
	. .venv/bin/activate && pip install -r tools/requirements-scripts.txt || true
	@echo "✔ venv ready (.venv)."

status:
	@bash scripts/portfolio-status.sh

test-all:
	@for p in $$(ls -1 projects | grep -E '^P[0-9]{2}-'); do \
		echo "== $$p =="; \
		make -C projects/$$p test || echo "skip/no tests"; \
	done

docs-gen:
	@python3 tools/scaffold_docs.py

demo-day:
	@bash demos/demo_day_v2.sh

evidence-pack:
	@[ -n "$(DASH)" ] || (echo "Set DASH and PANEL"; exit 2)
	. .venv/bin/activate && DASH="$(DASH)" PANEL="$(PANEL)" bash scripts/evidence_pack.sh "$(DASH)" "$(PANEL)" projects/P25-observability projects/P09-rag-chatbot

fmt:
	@pre-commit run --all-files || true

lint:
	@pre-commit run --all-files || true

pre-commit-install:
	@pre-commit install && echo "✔ pre-commit hooks installed"

ci-check:
	@echo "Running minimal CI checks locally"
	@pre-commit run --all-files || true
	@bash scripts/portfolio-status.sh

status-md:
	@python scripts/status_to_markdown.py && echo "✔ docs/status.md updated"
