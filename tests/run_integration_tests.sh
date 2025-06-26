#!/bin/bash
# Run integration tests with timeout - ACTUALLY RUN THEM (bypass @unittest.skip)
# Run from project root directory
cd "$(dirname "$0")/.."
echo "Running integration tests with skip decorators bypassed (with 60s timeout per test)..."
echo "WARNING: Some tests may hang - use Ctrl+C to interrupt if needed"

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
echo ""

# Create temporary versions of test files with skip decorators commented out
TEMP_DIR=$(mktemp -d)
echo "Creating temporary test files without skip decorators in: $TEMP_DIR"

# Copy test files and remove skip decorators
for test_file in tests/test_*.py; do
    if [[ ! "$test_file" =~ "_unit.py" ]]; then
        filename=$(basename "$test_file")
        # Comment out @unittest.skip lines and the following line if it contains a reason
        sed 's/^@unittest\.skip/#@unittest.skip/g' "$test_file" > "$TEMP_DIR/$filename"
        sed -i.bak 's/^@unittest\.skip/#@unittest.skip/g' "$TEMP_DIR/$filename"
        rm -f "$TEMP_DIR/$filename.bak" 2>/dev/null
    fi
done

# Set PYTHONPATH to include the src directory and temp directory  
export PYTHONPATH="$(pwd)/src:$(pwd):$PYTHONPATH"

# Run integration tests one by one with longer timeout
success_count=0
fail_count=0
timeout_count=0

for test_file in "$TEMP_DIR"/test_*.py; do
    if [[ -f "$test_file" ]]; then
        filename=$(basename "$test_file")
        echo "----------------------------------------"
        echo "Running $filename (timeout: 60s)..."
        echo "----------------------------------------"
        
        if timeout 60 python -m unittest "$test_file" -v; then
            echo "✅ PASSED: $filename"
            ((success_count++))
        else
            exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo "⏰ TIMEOUT: $filename"
                ((timeout_count++))
            else
                echo "❌ FAILED: $filename"
                ((fail_count++))
            fi
        fi
        echo ""
    fi
done

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Report results
echo "========================================"
echo "Integration Test Results:"
echo "✅ Passed: $success_count"
echo "❌ Failed: $fail_count"  
echo "⏰ Timeout: $timeout_count"
echo "========================================"

if [ $fail_count -eq 0 ] && [ $timeout_count -eq 0 ]; then
    echo "🎉 All integration tests passed!"
    exit 0
else
    echo "⚠️  Some integration tests failed or timed out"
    exit 1
fi