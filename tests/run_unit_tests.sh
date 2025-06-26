#!/bin/bash
# Run only unit tests (skip integration tests)
# Run from project root directory
cd "$(dirname "$0")/.."
echo "Running unit tests only..."
python -m unittest discover tests/ -p "test_*_unit.py" -v