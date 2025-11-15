# Repository Guidelines

## Project Layout & Responsibilities
- Core source lives in `src/travel_tools/`. The pipeline is split into `step1_filter.py`–`step4_generate_web.py`, all orchestrated by `launcher.py`. Each step should only touch its stage-specific folders (`data/{dest}/{source}/raw|filtered|scraped|merged` plus `outputs/{dest}/{source}/`).
- Shared helpers stay inside `src/travel_tools/utils/` (`file_ops.py`, `logger.py`, `validators.py`) and all runtime schemas belong to `types.py` so validation stays centralized.
- The viewer is now a standalone Vue + TypeScript app living in `web_client/`. Step 4 only emits `hotels.json`; the Vue bundle (built via `npm run build`) is copied into the `outputs/` root (index + assets) and asks the user which destination/source JSON to load.
- Config files (`config/destinations.json`, `config/settings.json`) define supported slugs and scraper/launch settings. Keep runtime-safe defaults there and document new keys.

## Tooling & Commands
- Install with `pip install -r requirements.txt` plus `pip install -r requirements-dev.txt`, then run `playwright install chromium`. `setup.sh` wraps the usual bootstrap.
- Preferred entry points are `python -m travel_tools.launcher` for the guided workflow or `python -m travel_tools.step{1..4}_*` for targeted debugging. CLI shorthands are provided via `pyproject.toml` (`travel-tools`, `tt-filter`, `tt-scrape`, `tt-merge`, `tt-generate-web`).
- Podman users can rely on the `Makefile` which proxies to `podman-run.sh`: `make run` for the launcher, `make filter DEST=cancun SOURCE=transat BUDGET=5000`, etc. `make test` shells into the test container, and `make serve` runs the static `python -m http.server 8000 -d outputs` instance.
- Build the Vue viewer by running `npm install && npm run build` inside `web_client/`; this writes `outputs/index.html` + `assets/`, so after serving `outputs/` you can open `http://localhost:8000/` to pick a destination/source JSON.

## Coding Standards
- Target Python 3.11 with full typing; `mypy` runs in strict mode (see `pyproject.toml`). Do not introduce dynamically typed helpers unless justified and guarded.
- Format with `black` (100 char line length) and lint using `ruff check src/`. Keep both clean before requesting review. Follow `snake_case` for modules/functions, `PascalCase` for models, and descriptive filenames like `budget_5000.json`.
- Prefer declarative intent-revealing comments around tricky logic (e.g., scraper retries) rather than restating code.

## Testing Expectations
- Pytest configuration lives in `pytest.ini`/`pyproject.toml` with `-v --cov=travel_tools --cov-report=html --cov-report=term`. Run `pytest` (or `pytest tests/unit/test_filter.py` when iterating) before committing. If you add IO-heavy flows, mirror them under `tests/integration/`.
- Fixtures belong in `tests/fixtures/` and are wired through `tests/conftest.py`; extend those JSON samples instead of embedding literal data in tests.
- Step-specific logic should be covered in the corresponding `tests/unit/test_*.py`. Add regression tests whenever schemas or file formats change.
- The Vue viewer has its own Vitest suite. Execute `npm run test` (or `npm run test:watch`) inside `web_client/` for UI changes.

## Data & Safety Practices
- The pipeline expects lowercase destination/source slugs defined in `config/destinations.json`. When onboarding a new location, update the config, scaffold `data/<dest>/<source>/raw/`, and note the addition in `README.md`.
- Treat `data/` and `outputs/` as user-owned. Never delete or overwrite existing artifacts unless the change is requested; instead, write new files (e.g., new budget JSON) or back up previous outputs. The shared viewer bundle now lives directly under `outputs/` (index + assets); avoid committing built assets.
- Keep real packages, credentials, and scraping cookies out of git. Only include sanitized fixtures. Review `config/settings.json` before pushing to avoid leaking personal defaults.

## Documentation, Commits & Reviews
- Existing docs (`README.md`, `QUICKSTART.md`, `PODMAN_GUIDE.md`, `CONTAINER_SUMMARY.md`, `IMPLEMENTATION_SUMMARY.md`) describe the workflow. Update them when changing UX, dependencies, or supported destinations/sources.
- Commit subjects should be imperative and scoped to the pipeline area (`scrape: add fallback rating parser`). PRs should outline the problem, summarize the fix, list commands run (`pytest`, `mypy src/`, `ruff check src/`, `black --check src/`), and include viewer screenshots/GIFs when UI changes occur. Call out any migrations impacting `data/` or `outputs/`.
