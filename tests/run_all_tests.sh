#!/bin/bash
# Comprehensive test runner - runs ALL tests with detailed feedback
# Run from project root directory
cd "$(dirname "$0")/.."
echo "Running ALL tests (unit + integration) with detailed feedback..."
echo "WARNING: Integration tests may take longer and require full app setup"

# Check for database for integration tests
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

if [ ! -f "$DB_PATH" ]; then
    echo "⚠️  Warning: Database not found at $DB_PATH"
    echo "   Integration tests may fail. Run 'ordb --help' first to set up database."
fi

echo "Using database at: $DB_PATH"
echo ""

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$(pwd)/src:$(pwd):$PYTHONPATH"

# Create Python script to run tests with detailed output
cat > run_detailed_tests.py << 'EOF'
import unittest
import sys
import importlib.util
from pathlib import Path
import os

def run_test_file_with_details(test_file):
    """Run a single test file with detailed output."""
    print(f"🔍 Loading: {test_file}")
    
    try:
        # Load the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = test_module
        spec.loader.exec_module(test_module)
        
        # Run the tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Count tests in this file
        test_count = suite.countTestCases()
        if test_count == 0:
            print(f"   📄 No tests found in {test_file}")
            return True, 0, 0, 0
        
        print(f"   🧪 Found {test_count} test(s)")
        
        # Run with detailed output
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
        result = runner.run(suite)
        
        # Count results
        tests_run = result.testsRun
        tests_passed = tests_run - len(result.failures) - len(result.errors)
        tests_failed = len(result.failures) + len(result.errors)
        
        # Print detailed failure information
        if result.failures:
            print(f"   💥 FAILURES in {test_file}:")
            for test, traceback in result.failures:
                print(f"      ❌ {test}: {traceback.strip()}")
        
        if result.errors:
            print(f"   🚨 ERRORS in {test_file}:")
            for test, traceback in result.errors:
                print(f"      💀 {test}: {traceback.strip()}")
        
        success = result.wasSuccessful()
        
        if success:
            print(f"   ✅ ALL PASSED: {tests_passed}/{tests_run}")
        else:
            print(f"   ❌ FAILED: {tests_passed} passed, {tests_failed} failed out of {tests_run}")
        
        return success, tests_run, tests_passed, tests_failed
        
    except Exception as e:
        print(f"   💀 EXCEPTION loading {test_file}: {e}")
        return False, 0, 0, 1
    finally:
        # Clean up module
        if "test_module" in sys.modules:
            del sys.modules["test_module"]

def main():
    """Run all test files with detailed feedback."""
    test_dir = Path("tests")
    test_files = sorted(test_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found in tests/ directory")
        return 1
    
    print(f"Found {len(test_files)} test files to run")
    print("=" * 60)
    
    total_files = len(test_files)
    total_tests_run = 0
    total_tests_passed = 0
    total_tests_failed = 0
    files_passed = 0
    files_failed = 0
    
    for test_file in test_files:
        filename = test_file.name
        print(f"\n📦 Running {filename}")
        print("-" * 50)
        
        success, tests_run, tests_passed, tests_failed = run_test_file_with_details(test_file)
        
        total_tests_run += tests_run
        total_tests_passed += tests_passed
        total_tests_failed += tests_failed
        
        if success and tests_run > 0:
            files_passed += 1
            print(f"✅ {filename}: PASSED")
        elif tests_run == 0:
            print(f"⚪ {filename}: NO TESTS")
        else:
            files_failed += 1
            print(f"❌ {filename}: FAILED")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"📁 Test files: {total_files}")
    print(f"📁 Files passed: {files_passed}")
    print(f"📁 Files failed: {files_failed}")
    print(f"🧪 Total tests: {total_tests_run}")
    print(f"✅ Tests passed: {total_tests_passed}")
    print(f"❌ Tests failed: {total_tests_failed}")
    
    if total_tests_failed == 0 and files_failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {total_tests_failed} test(s) failed across {files_failed} file(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the comprehensive test suite
python run_detailed_tests.py
exit_code=$?

# Clean up
rm -f run_detailed_tests.py

# Exit with the same code as the test runner
exit $exit_code