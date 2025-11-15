# Podman Guide for travelTools 🐳

Run travelTools in isolated containers without installing Python or dependencies on your system!

## Why Containers?

✅ **Clean System** - No Python packages installed locally
✅ **Reproducible** - Same environment everywhere
✅ **Isolated** - Each tool runs independently
✅ **Easy Cleanup** - Remove containers when done

## Prerequisites

Install Podman:

```bash
# Fedora/RHEL/CentOS
sudo dnf install podman

# Ubuntu/Debian
sudo apt-get install podman

# Verify installation
podman --version
```

## Quick Start (3 Steps)

### 1. Build Images

```bash
cd /home/cylus/Dev/travel/travelTools
./podman-build.sh
```

This builds 3 images:
- `traveltools:latest` - Main pipeline (~1.5 GB)
- `traveltools:dev` - Development environment
- `traveltools:test` - Testing environment

### 2. Add Data

```bash
mkdir -p data/cancun/transat/raw
cp /path/to/packages.json data/cancun/transat/raw/packages.json
```

### 3. Run Pipeline

```bash
./podman-run.sh pipeline
```

The interactive launcher will guide you through the steps!

## Available Images

### 1. Pipeline Image (`traveltools:latest`)

**Purpose:** Run the complete pipeline

**Contains:**
- Python 3.11
- All dependencies (Playwright, Pydantic, etc.)
- Chromium browser for scraping
- All pipeline scripts

**Usage:**
```bash
./podman-run.sh pipeline
```

### 2. Development Image (`traveltools:dev`)

**Purpose:** Interactive development with hot-reload

**Contains:**
- Everything from pipeline image
- Development tools (pytest, mypy, black, ruff)
- Git and vim
- Port 8000 exposed for web server

**Usage:**
```bash
./podman-run.sh dev
# Inside container:
python -m travel_tools.step1_filter --destination cancun --source transat --budget 5000
cd outputs/cancun/transat && python -m http.server 8000
```

### 3. Testing Image (`traveltools:test`)

**Purpose:** Run tests in isolation

**Contains:**
- Python 3.11
- All dependencies
- Test framework (pytest)

**Usage:**
```bash
./podman-run.sh test
./podman-run.sh test tests/unit/test_filter.py  # specific test
./podman-run.sh test -v --cov                   # with coverage
```

## Usage Examples

### Interactive Pipeline (Recommended)

```bash
./podman-run.sh pipeline
```

Prompts for:
- Destination (cancun, punta-cana, etc.)
- Source (transat, expedia, etc.)
- Budget (e.g., 5000)

Then runs all 4 steps with confirmations between each.

### Individual Steps

```bash
# Step 1: Filter packages
./podman-run.sh filter cancun transat 5000

# Step 2: Scrape Google Maps ratings
./podman-run.sh scrape cancun transat

# Step 3: Merge data
./podman-run.sh merge cancun transat

# Step 4: Generate web viewer
./podman-run.sh web cancun transat
```

### View Results

```bash
# Start web server on port 8080
./podman-run.sh serve 8080

# Then open: http://localhost:8080/cancun/transat/
```

### Development

```bash
# Start development container
./podman-run.sh dev

# Inside container, you can:
# - Edit code (changes reflect immediately via volume mount)
# - Run commands: python -m travel_tools.step1_filter ...
# - Start web server: cd outputs && python -m http.server 8000
# - Run tests: pytest
# - Type check: mypy src/
```

### Testing

```bash
# Run all tests
./podman-run.sh test

# Run specific test file
./podman-run.sh test tests/unit/test_filter.py

# Run with coverage
./podman-run.sh test --cov --cov-report=html
```

### Shell Access

```bash
# Open bash shell in pipeline container
./podman-run.sh shell

# Explore the container, run commands manually
```

## Using Podman Compose

If you have `podman-compose` installed:

```bash
# Install podman-compose
pip install podman-compose

# Start services
podman-compose -f podman-compose.yml up pipeline

# Run tests
podman-compose -f podman-compose.yml up test

# Start development
podman-compose -f podman-compose.yml up dev

# Start web server
podman-compose -f podman-compose.yml up webserver
# Then visit: http://localhost:8080
```

## Volume Mounts

Data is shared between host and containers:

- `./data` → `/app/data` (raw packages, filtered, scraped, merged)
- `./outputs` → `/app/outputs` (generated HTML viewers)
- `./src` → `/app/src` (dev only - for hot reload)
- `./tests` → `/app/tests` (dev/test only)

**Note:** The `:Z` suffix on volume mounts enables SELinux compatibility.

## Image Management

### List Images

```bash
podman images | grep traveltools
```

### Rebuild Single Image

```bash
# Rebuild main pipeline
podman build -t traveltools:latest -f Dockerfile .

# Rebuild dev image
podman build -t traveltools:dev -f Dockerfile.dev .

# Rebuild test image
podman build -t traveltools:test -f Dockerfile.test .
```

### Remove Images

```bash
# Remove all traveltools images and containers
./podman-run.sh clean

# Or manually:
podman rmi traveltools:latest traveltools:dev traveltools:test
```

## Complete Workflow Example

```bash
# 1. Build images (one time)
./podman-build.sh

# 2. Add your data
mkdir -p data/cancun/transat/raw
cp ../cancun/packages.json data/cancun/transat/raw/packages.json

# 3. Run step-by-step
./podman-run.sh filter cancun transat 5000
./podman-run.sh scrape cancun transat     # Takes ~5 min
./podman-run.sh merge cancun transat
./podman-run.sh web cancun transat

# 4. View results
./podman-run.sh serve 8080
# Open: http://localhost:8080/cancun/transat/

# Or run everything interactively:
./podman-run.sh pipeline
```

## Troubleshooting

### Issue: "Permission denied" on volume mounts

**Solution:** Add `:Z` suffix to enable SELinux relabeling (already in scripts)

```bash
-v ./data:/app/data:Z
```

### Issue: Container fails to start

**Solution:** Check logs

```bash
podman logs traveltools-pipeline
```

### Issue: Playwright fails in container

**Solution:** Already handled - Dockerfile installs all browser dependencies

### Issue: Port already in use

**Solution:** Use different port

```bash
./podman-run.sh serve 9000  # Use port 9000 instead
```

### Issue: Out of disk space

**Solution:** Clean up old images and containers

```bash
podman system prune -a
```

## Advantages vs Local Installation

| Aspect | Local Install | Podman Containers |
|--------|---------------|-------------------|
| System clutter | Many packages | None |
| Python version | System Python | Python 3.11 guaranteed |
| Dependencies | Global/venv | Isolated |
| Cleanup | Manual | `podman rmi` |
| Reproducibility | Environment-dependent | Always same |
| Multiple versions | Conflicts possible | Run any version |

## Advanced Usage

### Custom Budget Variable

```bash
# Set environment variable
export BUDGET=6000
./podman-run.sh filter cancun transat $BUDGET
```

### Run Multiple Destinations

```bash
# Process Cancun
./podman-run.sh pipeline  # Select: cancun

# Process Punta Cana
./podman-run.sh pipeline  # Select: punta-cana

# View both
./podman-run.sh serve 8080
```

### Mount Additional Volumes

```bash
podman run -it --rm \
  -v ./data:/app/data:Z \
  -v ./outputs:/app/outputs:Z \
  -v ./custom-config:/app/custom:Z \
  traveltools:latest \
  python -m travel_tools.launcher
```

## Performance Notes

- **First build:** ~5-10 minutes (downloads Python, Playwright, etc.)
- **Subsequent builds:** ~1-2 minutes (uses cache)
- **Container startup:** < 1 second
- **Scraping:** Same as local (~5 min for 50 hotels)

## Summary

**Easiest way to use:**
```bash
./podman-build.sh           # One time
./podman-run.sh pipeline    # Every time
./podman-run.sh serve 8080  # View results
```

**No Python installation needed on your system!** 🎉
