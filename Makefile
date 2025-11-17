.PHONY: help build run dev test clean serve shell viewer serve_viewer

MAX_REVIEWS ?= 10
DEST ?= cancun
SOURCE ?= transat
BUDGET ?= 5000
HEADLESS ?= true

ifneq (,$(wildcard .env))
include .env
export $(shell sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p' .env)
endif

# Default target
help:
	@echo "🌴 travelTools - Podman Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  make build          Build all Podman images"
	@echo ""
	@echo "Run:"
	@echo "  make run            Run interactive pipeline"
	@echo "  make dev            Start development container"
	@echo "  make test           Run tests"
	@echo "  make serve          Start web server (port 8080)"
	@echo "  make shell          Open bash shell in container"
	@echo ""
	@echo "Individual steps:"
	@echo "  make filter DEST=cancun SOURCE=transat BUDGET=5000"
	@echo "  make scrape DEST=cancun SOURCE=transat MAX_REVIEWS=10"
	@echo "  make summarize DEST=cancun SOURCE=transat   # requires GEMINI_API_KEY"
	@echo "  make merge DEST=cancun SOURCE=transat"
	@echo "  make web DEST=cancun SOURCE=transat"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove all containers and images"
	@echo "Viewer:"
	@echo "  make viewer         Build Vue frontend bundle"
	@echo "  make serve_viewer   Serve outputs/ (JSON + viewer) locally"
	@echo ""
	@echo "Examples:"
	@echo "  make build && make run"
	@echo "  make filter DEST=punta-cana BUDGET=6000"
	@echo "  make pipeline && make viewer && make serve_viewer"
	@echo "  make pipeline-all    # run all destinations/sources (host Python)"
	@echo ""

# Build all images
build:
	@./podman-build.sh

# Run interactive pipeline
run:
	@./podman-run.sh pipeline

# Start development container
dev:
	@./podman-run.sh dev

# Run tests
test:
	@./podman-run.sh test

# Individual steps
filter:
	@./podman-run.sh filter $(DEST) $(SOURCE) $(BUDGET)

scrape:
	@./podman-run.sh scrape $(DEST) $(SOURCE) $(HEADLESS) $(MAX_REVIEWS)

summarize:
	@./podman-run.sh summarize $(DEST) $(SOURCE)

merge:
	@./podman-run.sh merge $(DEST) $(SOURCE)

web:
	@./podman-run.sh web $(DEST) $(SOURCE)

# Start web server
serve:
	@./podman-run.sh serve $(PORT)

# Build Vue viewer bundle
viewer:
	@cd web_client && npm install && npm run build

# Serve outputs directory with built viewer
serve_viewer:
	@cd outputs && python -m http.server 8000

# Open shell in container
shell:
	@./podman-run.sh shell

# Clean up everything
clean:
	@./podman-run.sh clean

# All-in-one: filter -> scrape -> merge -> web
pipeline:
	@./podman-run.sh filter $(DEST) $(SOURCE) $(BUDGET)
	@./podman-run.sh scrape $(DEST) $(SOURCE) $(HEADLESS) $(MAX_REVIEWS)
	@if [ -n "$$GEMINI_API_KEY" ]; then \
		echo "🤖 GEMINI_API_KEY detected - running summarize step"; \
		./podman-run.sh summarize $(DEST) $(SOURCE); \
	else \
		echo "⚠️  Skipping summarize (set GEMINI_API_KEY to enable)"; \
	fi
	@./podman-run.sh merge $(DEST) $(SOURCE)
	@./podman-run.sh web $(DEST) $(SOURCE)
	@echo "✅ Pipeline complete!"
	@echo "View results with: make serve"

# Run all destinations/sources with default skip behavior (host env)
pipeline-all:
	@python -m travel_tools.launcher --all --budget $(BUDGET)
