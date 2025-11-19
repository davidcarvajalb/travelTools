#!/bin/bash
# Run travelTools with Podman

set -e

ENV_FILE_ARGS=""
if [ -f .env ]; then
  ENV_FILE_ARGS="--env-file .env"
fi

COMMAND=${1:-pipeline}
shift || true

case $COMMAND in
  pipeline)
    echo "🌴 Running travelTools Pipeline (Interactive)"
    ENV_ARGS=""
    if [ -n "$GEMINI_API_KEY" ]; then
      ENV_ARGS="-e GEMINI_API_KEY=$GEMINI_API_KEY"
    fi
    podman run -it --rm \
      -v ./data:/app/data:Z \
      -v ./outputs:/app/outputs:Z \
      $ENV_FILE_ARGS \
      $ENV_ARGS \
      traveltools:latest
    ;;

  dev)
    echo "🌴 Starting Development Container"
    echo "You'll have an interactive bash shell with hot-reload"
    podman run -it --rm \
      -v ./src:/app/src:Z \
      -v ./tests:/app/tests:Z \
      -v ./data:/app/data:Z \
      -v ./outputs:/app/outputs:Z \
      -v ./config:/app/config:Z \
      $ENV_FILE_ARGS \
      -p 8000:8000 \
      traveltools:dev
    ;;

  test)
    echo "🧪 Running Tests"
    podman run --rm \
      -v ./src:/app/src:Z \
      -v ./tests:/app/tests:Z \
      $ENV_FILE_ARGS \
      traveltools:test "$@"
    ;;

  filter)
    DEST=${1:-cancun}
    SOURCE=${2:-transat}
    BUDGET=${3:-5000}
    echo "🔍 Running Step 1: Filter ($DEST/$SOURCE, budget: \$$BUDGET)"
    podman run --rm \
      -v ./data:/app/data:Z \
      $ENV_FILE_ARGS \
      traveltools:latest \
      python -m travel_tools.step1_filter \
        --destination "$DEST" \
        --source "$SOURCE" \
        --budget "$BUDGET"
    ;;

  scrape)
    DEST=${1:-cancun}
    SOURCE=${2:-transat}
    HEADLESS=${3:-true}
    MAX_REVIEWS=${4:-10}
    echo "🕷️  Running Step 2: Scrape ($DEST/$SOURCE) (headless: $HEADLESS)"
    echo "Note: This may take several minutes..."
    podman run --rm \
      -v ./data:/app/data:Z \
      $ENV_FILE_ARGS \
      traveltools:latest \
      python -m travel_tools.step2_scrape \
        --destination "$DEST" \
        --source "$SOURCE" \
        --headless "$HEADLESS" \
        --max-reviews "$MAX_REVIEWS"
    ;;

  summarize)
    DEST=${1:-cancun}
    SOURCE=${2:-transat}
    MODEL=${3:-gemini-2.5-flash}
    RATE_LIMIT=${4:-1.0}
    echo "🤖 Running Step 2.5: AI Summarize ($DEST/$SOURCE) [model: $MODEL, rate-limit: ${RATE_LIMIT}s]"
    # Pass through GEMINI_API_KEY if set
    ENV_ARGS=""
    if [ -n "$GEMINI_API_KEY" ]; then
      ENV_ARGS="-e GEMINI_API_KEY=$GEMINI_API_KEY"
    fi
    podman run --rm \
      -v ./data:/app/data:Z \
      $ENV_FILE_ARGS \
      $ENV_ARGS \
      traveltools:latest \
      python -m travel_tools.step2_5_summarize \
        --destination "$DEST" \
        --source "$SOURCE" \
        --model "$MODEL" \
        --rate-limit "$RATE_LIMIT"
    ;;

  merge)
    DEST=${1:-cancun}
    SOURCE=${2:-transat}
    echo "🔀 Running Step 3: Merge ($DEST/$SOURCE)"
    podman run --rm \
      -v ./data:/app/data:Z \
      $ENV_FILE_ARGS \
      traveltools:latest \
      python -m travel_tools.step3_merge \
        --destination "$DEST" \
        --source "$SOURCE"
    ;;

  web)
    DEST=${1:-cancun}
    SOURCE=${2:-transat}
    echo "🌐 Running Step 4: Generate Web ($DEST/$SOURCE)"
    podman run --rm \
      -v ./data:/app/data:Z \
      -v ./outputs:/app/outputs:Z \
      $ENV_FILE_ARGS \
      traveltools:latest \
      python -m travel_tools.step4_generate_web \
        --destination "$DEST" \
        --source "$SOURCE"
    ;;

  serve)
    PORT=${1:-8080}
    echo "🌐 Starting web server on port $PORT"
    echo "View outputs at: http://localhost:$PORT"
    podman run --rm \
      -v ./outputs:/app/outputs:Z \
      $ENV_FILE_ARGS \
      -p "$PORT:8000" \
      -w /app/outputs \
      python:3.11-slim \
      python -m http.server 8000
    ;;

  shell)
    echo "🐚 Opening shell in container"
    # Pass through GEMINI_API_KEY if set
    ENV_ARGS=""
    if [ -n "$GEMINI_API_KEY" ]; then
      ENV_ARGS="-e GEMINI_API_KEY=$GEMINI_API_KEY"
    fi
    podman run -it --rm \
      -v ./data:/app/data:Z \
      -v ./outputs:/app/outputs:Z \
      $ENV_FILE_ARGS \
      $ENV_ARGS \
      traveltools:latest \
      /bin/bash
    ;;

  clean)
    echo "🧹 Cleaning up containers and images"
    podman ps -a | grep traveltools | awk '{print $1}' | xargs -r podman rm -f
    podman images | grep traveltools | awk '{print $3}' | xargs -r podman rmi -f
    echo "✓ Cleanup complete"
    ;;

  *)
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  pipeline              Run full interactive pipeline"
    echo "  dev                   Start development container"
    echo "  test [args]          Run tests (pass pytest args)"
    echo "  filter <dest> <src> <budget>   Run step 1: Filter"
    echo "  scrape <dest> <src>            Run step 2: Scrape"
    echo "  summarize <dest> <src>         Run step 2.5: AI Summarize"
    echo "  merge <dest> <src>             Run step 3: Merge"
    echo "  web <dest> <src>               Run step 4: Generate web"
    echo "  serve [port]         Start web server (default: 8080)"
    echo "  shell                Open bash shell in container"
    echo "  clean                Remove all containers and images"
    echo ""
    echo "Examples:"
    echo "  $0 pipeline                          # Interactive launcher"
    echo "  $0 filter cancun transat 5000       # Filter packages"
    echo "  $0 scrape cancun transat            # Scrape ratings"
    echo "  export GEMINI_API_KEY=xyz && $0 summarize cancun transat  # AI summarize"
    echo "  $0 serve 8080                       # View outputs"
    echo "  $0 test                             # Run all tests"
    echo "  $0 dev                              # Development shell"
    exit 1
    ;;
esac
