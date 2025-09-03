#!/bin/bash
# Setup script for LinkedIn Company Analysis Tool

set -e

echo "🚀 Setting up LinkedIn Company Analysis Tool..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Poetry installed!"
else
    echo "✅ Poetry found!"
fi

# Install dependencies using Poetry
echo "📚 Installing dependencies with Poetry..."
poetry install

echo "✅ Setup complete!"
echo ""
echo "🎯 Poetry-based development commands:"
echo "  • Run tests: poetry run pytest tests/ -v"
echo "  • Start server: poetry run uvicorn src.linkedin_analyzer.main:app --reload"
echo "  • Run demo: poetry run python demos/step_1/demo.py"
echo "  • Code formatting: poetry run black src/ tests/"
echo "  • Import sorting: poetry run isort src/ tests/"
echo "  • Type checking: poetry run mypy src/"
echo "  • Linting: poetry run flake8 src/ tests/"
echo ""
echo "🌐 Visit http://localhost:8000/docs for API documentation"
echo ""
echo "💡 You can also activate the Poetry shell: poetry shell"