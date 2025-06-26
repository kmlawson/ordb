#!/bin/bash
# Run integration tests with timeout
# Run from project root directory
cd "$(dirname "$0")/.."
echo "Running integration tests (with 30s timeout per test)..."

# Check for database in OS-appropriate location
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    if [[ -n "$APPDATA" ]]; then
        DB_PATH="$APPDATA/ordb/articles.db"
    elif [[ -n "$USERPROFILE" ]]; then
        DB_PATH="$USERPROFILE/ordb/articles.db"
    else
        DB_PATH="$HOME/ordb/articles.db"
    fi
else
    # Unix-like (Linux, macOS, etc.)
    DB_PATH="$HOME/.ordb/articles.db"
fi

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found at $DB_PATH"
    echo "Please run 'ordb --help' first to set up the database."
    exit 1
fi

echo "Using database at: $DB_PATH"

# Run integration tests one by one with timeout
for test_file in tests/test_*.py; do
    if [[ ! "$test_file" =~ "_unit.py" ]]; then
        echo "Running $test_file..."
        timeout 30 python -m unittest "$test_file" -v || echo "Test timed out or failed: $test_file"
    fi
done