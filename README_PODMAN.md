# Travel Tools 🌴 - Containerized Edition

A Python-based hotel research pipeline that runs in Podman containers - **no local Python installation required!**

## Two Ways to Run

### Option 1: Podman Containers (Recommended - Keep System Clean)

✅ No Python packages on your system
✅ Reproducible environment
✅ Easy cleanup

```bash
# 1. Build images (one time, ~5-10 min)
./podman-build.sh

# 2. Add data
mkdir -p data/cancun/transat/raw
cp /path/to/packages.json data/cancun/transat/raw/

# 3. Run pipeline
./podman-run.sh pipeline

# 4. View results
./podman-run.sh serve 8080
# Open: http://localhost:8080/cancun/transat/
```

**See [PODMAN_GUIDE.md](PODMAN_GUIDE.md) for complete documentation.**

### Option 2: Local Installation (Traditional)

Requires Python 3.11+ installed locally.

```bash
./setup.sh
source venv/bin/activate
python -m travel_tools.launcher
```

**See [README.md](README.md) for local installation guide.**

## Features

- ✅ Filter hotel packages by budget
- ✅ Scrape Google Maps ratings automatically
- ✅ Merge package data with ratings
- ✅ Generate interactive web viewer
- ✅ Support multiple destinations and sources
- ✅ Type-safe with Pydantic models
- ✅ Comprehensive test coverage

## Quick Command Reference

### Podman Commands

```bash
# Interactive pipeline
./podman-run.sh pipeline

# Individual steps
./podman-run.sh filter cancun transat 5000
./podman-run.sh scrape cancun transat
./podman-run.sh merge cancun transat
./podman-run.sh web cancun transat

# View results
./podman-run.sh serve 8080

# Development
./podman-run.sh dev

# Testing
./podman-run.sh test

# Cleanup
./podman-run.sh clean
```

### Local Commands

```bash
# Activate environment
source venv/bin/activate

# Interactive pipeline
python -m travel_tools.launcher

# Individual steps
python -m travel_tools.step1_filter --destination cancun --source transat --budget 5000
python -m travel_tools.step2_scrape --destination cancun --source transat
python -m travel_tools.step3_merge --destination cancun --source transat
python -m travel_tools.step4_generate_web --destination cancun --source transat
```

## Documentation

- **[PODMAN_GUIDE.md](PODMAN_GUIDE.md)** - Complete Podman/container guide
- **[README.md](README.md)** - Local installation guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup (local)
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built

## Project Structure

```
travelTools/
├── Dockerfile              # Main pipeline image
├── Dockerfile.dev          # Development image
├── Dockerfile.test         # Testing image
├── podman-compose.yml      # Podman Compose config
├── podman-build.sh         # Build all images
├── podman-run.sh           # Run containers
├── src/travel_tools/       # Source code
├── data/                   # Input/processed data
└── outputs/                # Generated HTML viewers
```

## Supported Destinations

- **cancun** - Cancun, Mexico
- **punta-cana** - Punta Cana, Dominican Republic
- **riviera-maya** - Riviera Maya, Mexico

## Web Viewer Features

- 🔍 Search hotels by name
- 💰 Filter by price range
- ⭐ Filter by Google rating & stars
- 📊 Sort by any column
- 📦 Expand to see all package options
- 🔄 Reset all filters
- 📱 Responsive design

## Comparison: Podman vs Local

| Feature | Podman | Local |
|---------|--------|-------|
| System impact | None | Packages installed |
| Setup time | 5-10 min (one time) | 5 min |
| Disk space | ~1.5 GB images | ~500 MB venv |
| Performance | Same | Same |
| Cleanup | Easy (podman rmi) | Manual (rm venv) |
| Updates | Rebuild image | pip install |

## Getting Started

**For Podman users (recommended):**
1. Install Podman: `sudo dnf install podman`
2. Read [PODMAN_GUIDE.md](PODMAN_GUIDE.md)
3. Run `./podman-build.sh`
4. Run `./podman-run.sh pipeline`

**For local installation:**
1. Ensure Python 3.11+ installed
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Run `./setup.sh`
4. Run `python -m travel_tools.launcher`

## License

MIT

## Author

Created for personal travel research automation
