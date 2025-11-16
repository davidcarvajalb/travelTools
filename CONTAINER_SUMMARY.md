# Container Setup Summary

## ✅ Containerization Complete!

The travelTools project now runs in **Podman containers** - keeping your system completely clean!

## What Was Created

### Container Images (3 Images)

1. **traveltools:latest** (~1.5 GB)
   - Main pipeline image
   - Python 3.11 + all dependencies
   - Playwright + Chromium browser
   - Ready to run full pipeline

2. **traveltools:dev** (~1.7 GB)
   - Development environment
   - Everything from main + dev tools
   - Git, vim, pytest, mypy, black, ruff
   - Hot-reload via volume mounts

3. **traveltools:test** (~800 MB)
   - Minimal testing image
   - Python + test dependencies
   - Fast test execution

### Dockerfiles

- **Dockerfile** - Main pipeline image
- **Dockerfile.dev** - Development image with tools
- **Dockerfile.test** - Testing-only image
- **.dockerignore** - Excludes unnecessary files

### Orchestration

- **docker-compose.yml** - Docker Compose configuration
- **podman-compose.yml** - Podman Compose (with :Z for SELinux)

### Scripts

- **podman-build.sh** - Build all 3 images
- **podman-run.sh** - Run any container/command
- **Makefile** - Convenient make commands

### Documentation

- **PODMAN_GUIDE.md** - Complete Podman usage guide
- **README_PODMAN.md** - Quick reference
- **CONTAINER_SUMMARY.md** - This file

## Quick Start

### 1. Build Images (One Time)

```bash
./podman-build.sh
# Or: make build
```

**Time:** 5-10 minutes
**Result:** 3 images (~4 GB total)

### 2. Add Data

```bash
mkdir -p data/cancun/transat/raw
cp /path/to/packages.json data/cancun/transat/raw/
```

### 3. Run Pipeline

```bash
./podman-run.sh pipeline
# Or: make run
# Optional: export GEMINI_API_KEY=your_key_here to enable AI summaries during the run
```

### 4. View Results

```bash
./podman-run.sh serve 8080
# Or: make serve
# Open: http://localhost:8080/cancun/transat/
```

## All Available Commands

### Using Scripts

```bash
# Build
./podman-build.sh

# Run full pipeline (interactive)
./podman-run.sh pipeline

# Individual steps
./podman-run.sh filter cancun transat 5000
./podman-run.sh scrape cancun transat
./podman-run.sh summarize cancun transat   # requires GEMINI_API_KEY
./podman-run.sh merge cancun transat
./podman-run.sh web cancun transat

# Development
./podman-run.sh dev

# Testing
./podman-run.sh test
./podman-run.sh test tests/unit/test_filter.py

# View outputs
./podman-run.sh serve 8080

# Shell access
./podman-run.sh shell

# Cleanup
./podman-run.sh clean
```

### Using Makefile

```bash
# Build
make build

# Run
make run

# Individual steps
make filter DEST=cancun SOURCE=transat BUDGET=5000
make scrape DEST=cancun SOURCE=transat
make summarize DEST=cancun SOURCE=transat    # requires GEMINI_API_KEY
make merge DEST=cancun SOURCE=transat
make web DEST=cancun SOURCE=transat

# Development
make dev

# Testing
make test

# View outputs
make serve PORT=8080

# Shell
make shell

# Cleanup
make clean
```

### Using Podman Compose

```bash
# Install podman-compose first
pip install podman-compose

# Run services
podman-compose -f podman-compose.yml up pipeline
podman-compose -f podman-compose.yml up dev
podman-compose -f podman-compose.yml up test
podman-compose -f podman-compose.yml up webserver
```

## Volume Mounts

All containers share these volumes:

| Host | Container | Purpose |
|------|-----------|---------|
| `./data` | `/app/data` | Raw & processed data |
| `./outputs` | `/app/outputs` | Generated HTML viewers |
| `./src` | `/app/src` | Source code (dev only) |
| `./tests` | `/app/tests` | Tests (dev/test only) |
| `./config` | `/app/config` | Configuration (dev only) |

**Note:** The `:Z` suffix enables SELinux compatibility on Fedora/RHEL.

## Image Sizes

```
REPOSITORY           TAG      SIZE
traveltools          latest   ~1.5 GB
traveltools          dev      ~1.7 GB
traveltools          test     ~800 MB
```

## Workflow Examples

### Example 1: Complete Pipeline

```bash
# Build images (once)
make build

# Add data
mkdir -p data/cancun/transat/raw
cp ../cancun/packages.json data/cancun/transat/raw/

# Run interactively
make run
# Follow prompts: destination=cancun, source=transat, budget=5000

# View results
make serve
# Open http://localhost:8080/cancun/transat/
```

### Example 2: Step-by-Step Execution

```bash
# Run each step individually
make filter DEST=cancun SOURCE=transat BUDGET=5000
make scrape DEST=cancun SOURCE=transat    # ~5 minutes
make merge DEST=cancun SOURCE=transat
make web DEST=cancun SOURCE=transat
make serve
```

### Example 3: Development

```bash
# Start dev container
make dev

# Inside container:
$ python -m travel_tools.step1_filter --destination cancun --source transat --budget 5000
$ pytest tests/unit/test_filter.py
$ mypy src/
$ black src/
$ cd outputs/cancun/transat && python -m http.server 8000
```

### Example 4: Testing

```bash
# Run all tests
make test

# Run specific test
./podman-run.sh test tests/unit/test_filter.py

# Run with coverage
./podman-run.sh test --cov --cov-report=html
```

## Benefits vs Local Installation

### Podman Containers ✅

- **No system pollution** - Zero packages on host
- **Reproducible** - Exact same environment
- **Isolated** - Can't break system Python
- **Easy cleanup** - `podman rmi` removes everything
- **Multiple versions** - Run different versions side-by-side
- **Portable** - Share images with others

### Local Installation ❌

- Installs ~50 packages globally or in venv
- Environment depends on system Python
- Risk of conflicts with other projects
- Cleanup requires manual deletion
- Hard to share exact environment

## Disk Space

- **Images:** ~4 GB (one time)
- **Data:** Depends on your packages (typically < 100 MB)
- **Outputs:** ~1 MB per destination/source
- **Total:** ~4-5 GB

To free space:
```bash
make clean              # Remove traveltools containers/images
podman system prune -a  # Remove all unused images/containers
```

## Performance

- **Build time (first):** 5-10 minutes
- **Build time (cached):** 1-2 minutes
- **Container startup:** < 1 second
- **Pipeline execution:** Same as local
  - Filter: < 1 second
  - Scrape: ~5 minutes for 50 hotels
  - Merge: < 1 second
  - Generate web: < 1 second

## Troubleshooting

### Port already in use
```bash
make serve PORT=9000  # Use different port
```

### Permission denied on volumes
```bash
# Already handled with :Z suffix in scripts
```

### Out of disk space
```bash
podman system df       # Check usage
podman system prune -a # Clean up
```

### Container won't start
```bash
podman logs traveltools-pipeline
```

## Advanced Usage

### Custom environment variables

```bash
DEST=punta-cana SOURCE=sunwing BUDGET=6000 make filter
```

### Run with different Podman options

```bash
podman run -it --rm \
  -v ./data:/app/data:Z \
  -v ./outputs:/app/outputs:Z \
  --memory=4g \
  --cpus=2 \
  traveltools:latest \
  python -m travel_tools.launcher
```

### Export/Import images

```bash
# Export
podman save traveltools:latest -o traveltools.tar

# Import on another machine
podman load -i traveltools.tar
```

## Comparison Table

| Task | Podman Command | Local Command |
|------|----------------|---------------|
| Setup | `make build` (once) | `./setup.sh` |
| Run pipeline | `make run` | `python -m travel_tools.launcher` |
| Run tests | `make test` | `pytest` |
| View results | `make serve` | `cd outputs && python -m http.server` |
| Cleanup | `make clean` | `rm -rf venv/` |

## Files Created for Containers

```
travelTools/
├── Dockerfile                  # Main image
├── Dockerfile.dev              # Dev image
├── Dockerfile.test             # Test image
├── .dockerignore               # Exclude files
├── docker-compose.yml          # Docker Compose
├── podman-compose.yml          # Podman Compose (with :Z)
├── podman-build.sh             # Build script
├── podman-run.sh               # Run script
├── Makefile                    # Make commands
├── PODMAN_GUIDE.md             # Complete guide
├── README_PODMAN.md            # Quick reference
└── CONTAINER_SUMMARY.md        # This file
```

## Next Steps

1. **Build images:** `make build`
2. **Add data:** Copy packages.json to `data/` directory
3. **Run pipeline:** `make run`
4. **View results:** `make serve`

**Your system stays completely clean!** 🎉

## Documentation

- **[PODMAN_GUIDE.md](PODMAN_GUIDE.md)** - Detailed Podman guide
- **[README_PODMAN.md](README_PODMAN.md)** - Quick reference
- **[README.md](README.md)** - Original local installation guide
