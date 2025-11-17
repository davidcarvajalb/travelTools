# Travel Tools 🌴

A Python-based hotel research pipeline that automates filtering, scraping, and analyzing hotel package data with an interactive web viewer.

## Features

- ✅ Filter hotel packages by budget
- ✅ Scrape Google Maps ratings automatically (Playwright)
- ✅ Merge package data with ratings
- ✅ Optional AI review summaries with Google Gemini
- ✅ Generate interactive web viewer with filters and sorting
- ✅ Shared Vue + TypeScript viewer powered by Vitest
- ✅ Support multiple destinations and package sources
- ✅ Type-safe with Pydantic models
- ✅ Comprehensive test coverage
- ✅ Step-by-step interactive launcher

## Quick Start

### Installation

```bash
# Navigate to project directory
cd /home/cylus/Dev/travel/travelTools

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Playwright browsers
playwright install chromium

# Install viewer dependencies (Node 18+)
cd web_client
npm install
cd ..
```

### Setup Data

Place your raw package data in the appropriate directory:

```bash
# Example: Cancun packages from Transat
mkdir -p data/cancun/transat/raw
cp /path/to/packages.json data/cancun/transat/raw/packages.json
```

### Run the Pipeline

**Option 1: Interactive Launcher (Recommended)**

```bash
python -m travel_tools.launcher
```

The launcher will:
1. Prompt for destination, source, and budget
2. Offer optional AI summarization (Step 2.5) if you have a GEMINI_API_KEY
3. Run each step sequentially (filter → scrape → summarize → merge → normalize → generate web)
4. Ask for confirmation between steps
5. Generate the final web viewer

**Option 2: Individual Steps**

```bash
# Step 1: Filter by budget
python -m travel_tools.step1_filter --destination cancun --source transat --budget 5000

# Step 2: Scrape Google Maps ratings (skips hotels with existing rating/reviews by default)
python -m travel_tools.step2_scrape --destination cancun --source transat
# Add --force-scrape to re-run everything, or --hotel "Exact Hotel" to target one hotel

# Step 2.5: Summarize reviews with Gemini (requires GEMINI_API_KEY)
python -m travel_tools.step2_5_summarize --destination cancun --source transat
# Default: skips hotels that already have review_summary; add --force-summarize to regenerate
# Tip: export GEMINI_API_KEY=your_key_here before running.
# Tip: add --hotel "Exact Hotel Name" to summarize only one hotel

# Step 3: Merge data
python -m travel_tools.step3_merge --destination cancun --source transat

# Step 4: Generate hotels.json for the viewer
python -m travel_tools.step4_generate_web --destination cancun --source transat
```

Copy-paste commands with the common flags (replace destination/source as needed):
```bash
# Step 1: filter
python -m travel_tools.step1_filter \
  --destination cancun \
  --source transat \
  --budget 5000

# Step 2: scrape
python -m travel_tools.step2_scrape \
  --destination cancun \
  --source transat \
  --headless true \
  --max-reviews 200

# Step 2.5: summarize (requires GEMINI_API_KEY or --api-key)
python -m travel_tools.step2_5_summarize \
  --destination cancun \
  --source transat \
  --model gemini-2.5-flash-lite \
  --rate-limit 1.0 \
  --hotel-name "Exact Hotel (optional)" \
  --skip-existing-summaries \
  --max-reviews-per-hotel 150 \
  --max-new-summaries 5

python -m travel_tools.step2_5_summarize \
  --destination punta-cana \
  --source transat \
  --model gemini-2.5-pro \
  --hotel-name "BlueBay Villas Doradas" \
  --skip-existing-summaries


python -m travel_tools.step2_5_summarize \
  --destination punta-cana \
  --source transat \
  --model gemini-2.5-flash-lite \
  --rate-limit 60 \
  --skip-existing-summaries

# Step 3: merge
python -m travel_tools.step3_merge \
  --destination cancun \
  --source transat

# Step 3.5: normalize for web (new fields, HTTPS thumbnails, defaults)
python -m travel_tools.step3_5_normalize \
  --destination cancun \
  --source transat

# Step 4: generate web
python -m travel_tools.step4_generate_web \
  --destination cancun \
  --source transat
```

Flags per step (for reference):
- `step1_filter`: `--destination`, `--source`, `--budget`
- `step2_scrape`: `--destination`, `--source`, `--headless {true|false}`, `--max-reviews`, `--hotel`, `--force-scrape`
- `step2_5_summarize`: `--destination`, `--source`, `--api-key`, `--model`, `--rate-limit`, `--hotel`, `--force-summarize`, `--max-reviews-per-hotel`, `--max-new-summaries`, `--test-single-hotel`
- `step3_merge`: `--destination`, `--source`, `--hotel`
- `step3_5_normalize`: `--destination`, `--source`
- `step4_generate_web`: `--destination`, `--source`

### Run Everything (all destinations/sources)

Process every destination/source declared in `config/destinations.json`, skipping scrape/summarize when data already exists (use `--force-scrape` / `--force-summarize` to override):

```bash
python -m travel_tools.launcher --all --budget 5000
# or
make pipeline-all BUDGET=5000
```

### View Results

The Vue viewer is shared across all destinations and loads the JSON produced in `outputs/<destination>/<source>/hotels.json`.

```bash
# One-time install & build the viewer bundle
cd web_client
npm install
npm run build  # emits index.html + assets into outputs/

# Serve the entire outputs directory
cd ../outputs
python -m http.server 8000
# Visit http://localhost:8000/ and pick your destination/source
```

For rapid iteration you can run a dev server that proxies directly to the JSON files:

```bash
cd web_client
npm install
npm run dev
# Visit the printed URL (defaults to http://localhost:5173)
```

## Project Structure

```
travelTools/
├── src/travel_tools/       # Source code
│   ├── step1_filter.py     # Filter packages by budget
│   ├── step2_scrape.py     # Scrape Google Maps ratings
│   ├── step3_merge.py      # Merge packages with ratings
│   ├── step4_generate_web.py # Generate web viewer
│   ├── launcher.py         # Interactive pipeline launcher
│   ├── types.py            # Pydantic models
│   └── utils/              # Utility modules
│
├── data/                   # Data organized by destination/source
│   └── {destination}/
│       └── {source}/
│           ├── raw/        # Original package data
│           ├── filtered/   # Budget-filtered packages
│           ├── scraped/    # Google Maps ratings
│           └── merged/     # Final merged data
│
├── outputs/                # Generated data + viewer bundle
│   ├── {destination}/{source}/hotels.json  # Data consumed by the viewer
│   ├── assets/             # Built Vue assets (npm run build)
│   └── index.html          # Viewer entrypoint
│
├── tests/                  # Test suite
├── config/                 # Configuration files
└── web_client/             # Vue + TypeScript viewer
```

## Data Flow

```
Step 1: Filter
  Input:  data/cancun/transat/raw/packages.json
  Output: data/cancun/transat/filtered/budget_5000.json
  ↓
Step 2: Scrape
  Input:  budget_5000.json
  Output: data/cancun/transat/scraped/google_ratings.json
  ↓
Step 2.5: AI Summaries
  Input:  google_ratings.json
  Output: data/cancun/transat/scraped/ratings_with_summaries.json
  ↓
Step 3: Merge
  Input:  budget_5000.json + ratings_with_summaries.json (or google_ratings.json fallback)
  Output: data/cancun/transat/merged/final_data.json
  ↓
Step 4: Generate Web
  Input:  final_data.json
  Output: outputs/cancun/transat/hotels.json
```

## Supported Destinations

- **cancun** - Cancun, Mexico
- **punta-cana** - Punta Cana, Dominican Republic
- **riviera-maya** - Riviera Maya, Mexico

## Supported Package Sources

- **transat** - Transat packages
- **expedia** - Expedia packages
- **sunwing** - Sunwing packages

## Web Viewer Features

The generated HTML viewer includes:

- 🧭 **Destination picker** - Enter a destination/source to load its `hotels.json`
- 🔍 **Search** - Find hotels by name
- 💰 **Price filter** - Set min/max price range
- ⭐ **Rating filter** - Filter by minimum Google rating
- 🏨 **Stars filter** - Filter by hotel star rating
- 📊 **Sorting** - Sort by price, rating, reviews, or stars
- 📦 **Package details** - Expandable view of all packages
- 🔄 **Reset** - One-click filter reset
- 📱 **Responsive** - Works on desktop/mobile

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/unit/test_filter.py

# Watch mode
pytest --watch
```

### Viewer (Vue) Tests

```bash
cd web_client
npm install
npm run test        # run Vitest suite once
npm run test:watch  # watch mode during development
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type check
mypy src/
```

## Adding a New Destination

1. Add to `config/destinations.json`:

```json
{
  "jamaica": {
    "display_name": "Jamaica",
    "country": "Jamaica",
    "sources": ["transat"]
  }
}
```

2. Create data directory:

```bash
mkdir -p data/jamaica/transat/raw
```

3. Add package data:

```bash
cp /path/to/jamaica_packages.json data/jamaica/transat/raw/packages.json
```

4. Run pipeline:

```bash
python -m travel_tools.launcher
# Select: jamaica, transat, $5000
```

## Troubleshooting

### Playwright installation fails

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libnss3 libatk1.0-0 libatk-bridge2.0-0

# Then install Playwright browsers
playwright install chromium
```

### Google Maps blocks scraping

- Increase retry delay in `config/settings.json`
- Run scraper with `--headless false` to debug
- Check if hotel names are correct

### HTML viewer doesn't load

- Ensure JSON is valid: `python -m json.tool outputs/cancun/transat/hotels.json`
- Try opening with local server instead of `file://`
- Check browser console for errors

## Migration from Old Tools

If you have existing data from the old JavaScript tools:

```bash
# Copy existing Cancun data
mkdir -p data/cancun/transat/raw
cp ../cancun/packages.json data/cancun/transat/raw/packages.json

# Copy existing Punta Cana data
mkdir -p data/punta-cana/transat/raw
cp ../puntaCana/packages.json data/punta-cana/transat/raw/packages.json

# Run pipeline
python -m travel_tools.launcher
```

## License

MIT

## Author

Created for personal travel research automation
