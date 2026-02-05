#!/bin/bash
set -e

echo "=== Running verification ==="
echo ""

echo "1. Running test suite..."
pytest

echo ""
echo "2. Checking project structure..."
if command -v tree &> /dev/null; then
    tree -L 2 -I '__pycache__|*.pyc|venv|htmlcov|.pytest_cache'
else
    echo "  (tree not installed, skipping directory view)"
    ls -d */
fi

echo ""
echo "3. Verifying imports..."
python -c "from display import PygameDisplay; print('✓ Display imports')"
python -c "from input import KeyboardInput; print('✓ Input imports')"
python -c "from game import App; print('✓ Game imports')"
python -c "from data import Database; print('✓ Data imports')"
python -c "from config import Config; print('✓ Config imports')"

echo ""
echo "=== All checks passed! ==="
echo ""
echo "Run the app with: python main.py"
