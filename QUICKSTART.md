# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd /home/cylus/Dev/travel/travelTools

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -e .
pip install playwright
playwright install chromium

# 4. Verify installation
python -m travel_tools.launcher --help
```

## First Run with Existing Data

### Option A: Use Existing Cancun Data

```bash
# 1. Copy existing data
mkdir -p data/cancun/transat/raw
cp ../cancun/packages.json data/cancun/transat/raw/packages.json

# 2. Run pipeline
python -m travel_tools.launcher

# When prompted:
# - Destination: cancun
# - Source: transat
# - Budget: 5000

# 3. View results
cd web_client
npm install
npm run build
cd ../outputs
python -m http.server 8000
# Visit http://localhost:8000/ and pick cancun + transat
```

### Option B: Use Existing Punta Cana Data

```bash
# 1. Copy existing data
mkdir -p data/punta-cana/transat/raw
cp ../puntaCana/packages.json data/punta-cana/transat/raw/packages.json

# 2. Run pipeline
python -m travel_tools.launcher

# When prompted:
# - Destination: punta-cana
# - Source: transat
# - Budget: 5000

# 3. View results
cd web_client
npm install
npm run build
cd ../outputs
python -m http.server 8000
# Visit http://localhost:8000/ and pick punta-cana + transat
```

## Manual Step-by-Step Run

If you prefer to run each step individually:

```bash
# Step 1: Filter packages by budget
python -m travel_tools.step1_filter \\
  --destination cancun \\
  --source transat \\
  --budget 5000

# Step 2: Scrape Google Maps ratings (takes ~5 min for 50 hotels)
python -m travel_tools.step2_scrape \\
  --destination cancun \\
  --source transat

# Step 3: Merge data
python -m travel_tools.step3_merge \\
  --destination cancun \\
  --source transat

# Step 4: Generate hotels.json for the viewer
python -m travel_tools.step4_generate_web \\
  --destination cancun \\
  --source transat
```

## Viewing the Results

1. Build the Vue viewer (one-time install):

```bash
cd web_client
npm install
npm run build  # emits the viewer into outputs/viewer
```

2. Serve the outputs directory:

```bash
cd ../outputs
python -m http.server 8000
# Visit http://localhost:8000/ and choose your destination & source
```

For day-to-day development you can instead run `npm run dev` from `web_client/` to start Vite's dev server (http://localhost:5173) and load JSON files directly.

## Web Viewer Features

Once the HTML viewer opens, you can:

- 🔍 **Search** hotels by name
- 💰 **Filter** by price range (min/max)
- ⭐ **Filter** by Google rating
- 🏨 **Filter** by star rating
- 📊 **Sort** by clicking column headers
- 📦 **Expand** hotel rows to see all package options
- 🔄 **Reset** all filters

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/unit/test_filter.py
```

## Common Issues

### Issue: "playwright not found"

```bash
playwright install chromium
```

### Issue: "Module not found: travel_tools"

```bash
# Make sure you installed in editable mode
pip install -e .
```

### Issue: "No such file: packages.json"

```bash
# Ensure data is in correct location
ls data/cancun/transat/raw/packages.json
```

## Next Steps

- Add more destinations in `config/destinations.json`
- Adjust scraper settings in `config/settings.json`
- Compare multiple sources (Transat vs Expedia)
- Run pipeline on different budgets

## Getting Help

- Full documentation: See `README.md`
- Project spec: See `../travelTools_PROJECT_SPEC.md`
- Run any command with `--help` flag
