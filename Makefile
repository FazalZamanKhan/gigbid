.PHONY: dev test eval seed demo lint report-draft

dev:
	uvicorn apps.api.main:app --reload --port 8000

test:
	python -m pytest -q

eval:
	@echo "GigSim starter dev set is required before measured evaluation can run." && exit 2

seed:
	@echo "Place the instructor-provided GigSim and persona data under gigsim/ and data/personas/." && exit 2

demo:
	GIGBID_MARKETPLACE=demo uvicorn apps.api.main:app --port 8000

lint:
	python -m compileall -q agent apps rag mcp_servers

report-draft:
	python tools/build_interim_report.py
