#!/bin/bash
# Build all Podman images for travelTools

set -e

echo "🌴 Building travelTools Podman Images"
echo "======================================"

# Build main pipeline image
echo ""
echo "Building main pipeline image..."
podman build -t traveltools:latest -f Dockerfile .
echo "✓ Built: traveltools:latest"

# Build development image
echo ""
echo "Building development image..."
podman build -t traveltools:dev -f Dockerfile.dev .
echo "✓ Built: traveltools:dev"

# Build testing image
echo ""
echo "Building testing image..."
podman build -t traveltools:test -f Dockerfile.test .
echo "✓ Built: traveltools:test"

echo ""
echo "======================================"
echo "✅ All images built successfully!"
echo ""
echo "Available images:"
podman images | grep traveltools

echo ""
echo "Next steps:"
echo "  1. Run pipeline: ./podman-run.sh pipeline"
echo "  2. Development: ./podman-run.sh dev"
echo "  3. Tests: ./podman-run.sh test"
echo ""
