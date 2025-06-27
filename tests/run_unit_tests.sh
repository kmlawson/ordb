#!/bin/bash
# Unit test runner - runs ONLY unit tests (excludes integration tests) with detailed feedback
# Run from project root directory
cd "$(dirname "$0")/.."
echo "Running UNIT tests only (excludes integration tests) with detailed feedback..."

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$(pwd)/src:$(pwd):$PYTHONPATH"

# Create Python script to run only unit tests with detailed output
cat > run_unit_tests_detailed.py << 'EOF'
import unittest
import sys
import importlib.util
from pathlib import Path
import os

def is_unit_test_file(test_file):
    """Determine if a test file contains unit tests (not integration tests)."""
    # Files ending with _unit.py are definitely unit tests
    if test_file.name.endswith('_unit.py'):
        return True
    
    # Files NOT ending with _unit.py are likely integration tests
    # But let's check for specific integration test indicators
    integration_indicators = [
        'test_all_examples_and_config.py',
        'test_character_replacement.py', 
        'test_compact_inflections.py',
        'test_comprehensive_functionality.py',
        'test_config_wizard_completeness.py',
        'test_database_integrity.py',
        'test_display_flags.py',
        'test_etymology_flags.py',
        'test_inflection_flags.py',
        'test_interactive_fuzzy_search.py',
        'test_only_examples_expressions.py',
        'test_pagination.py',
        'test_platform_paths.py',
        'test_word_filters.py'
    ]
    
    return test_file.name not in integration_indicators

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
            return True, 0, 0, 0, 0
        
        print(f"   🧪 Found {test_count} test(s)")
        
        # Run with detailed output
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
        result = runner.run(suite)
        
        # Count results
        tests_run = result.testsRun
        tests_passed = tests_run - len(result.failures) - len(result.errors) - len(result.skipped)
        tests_failed = len(result.failures) + len(result.errors)
        tests_skipped = len(result.skipped)
        
        # Print detailed failure information
        if result.failures:
            print(f"   💥 FAILURES in {test_file}:")
            for test, traceback in result.failures:
                print(f"      ❌ {test}:")
                print(f"         {traceback.strip()}")
        
        if result.errors:
            print(f"   🚨 ERRORS in {test_file}:")
            for test, traceback in result.errors:
                print(f"      💀 {test}:")
                print(f"         {traceback.strip()}")
        
        if result.skipped:
            print(f"   ⏭️  SKIPPED in {test_file}:")
            for test, reason in result.skipped:
                print(f"      ⚪ {test}: {reason}")
        
        success = result.wasSuccessful()
        
        if success:
            if tests_skipped > 0:
                print(f"   ✅ PASSED: {tests_passed}/{tests_run} (skipped: {tests_skipped})")
            else:
                print(f"   ✅ ALL PASSED: {tests_passed}/{tests_run}")
        else:
            print(f"   ❌ FAILED: {tests_passed} passed, {tests_failed} failed, {tests_skipped} skipped out of {tests_run}")
        
        return success, tests_run, tests_passed, tests_failed, tests_skipped
        
    except Exception as e:
        print(f"   💀 EXCEPTION loading {test_file}: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, 0, 1, 0
    finally:
        # Clean up module
        if "test_module" in sys.modules:
            del sys.modules["test_module"]

def main():
    """Run only unit test files with detailed feedback."""
    test_dir = Path("tests")
    all_test_files = sorted(test_dir.glob("test_*.py"))
    
    # Filter to only unit test files
    unit_test_files = [f for f in all_test_files if is_unit_test_file(f)]
    integration_test_files = [f for f in all_test_files if not is_unit_test_file(f)]
    
    if not unit_test_files:
        print("❌ No unit test files found in tests/ directory")
        return 1
    
    print(f"Found {len(all_test_files)} total test files:")
    print(f"  🧪 {len(unit_test_files)} unit test files (will be run)")
    print(f"  🔌 {len(integration_test_files)} integration test files (excluded)")
    
    if integration_test_files:
        print(f"\n📋 Excluded integration test files:")
        for f in integration_test_files:
            print(f"     🔌 {f.name}")
    
    print("\n" + "=" * 60)
    print("🧪 RUNNING UNIT TESTS ONLY")
    print("=" * 60)
    
    total_files = len(unit_test_files)
    total_tests_run = 0
    total_tests_passed = 0
    total_tests_failed = 0
    total_tests_skipped = 0
    files_passed = 0
    files_failed = 0
    
    for test_file in unit_test_files:
        filename = test_file.name
        print(f"\n📦 Running {filename}")
        print("-" * 50)
        
        success, tests_run, tests_passed, tests_failed, tests_skipped = run_test_file_with_details(test_file)
        
        total_tests_run += tests_run
        total_tests_passed += tests_passed
        total_tests_failed += tests_failed
        total_tests_skipped += tests_skipped
        
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
    print("🏁 UNIT TEST RESULTS")
    print("=" * 60)
    print(f"📁 Unit test files: {total_files}")
    print(f"📁 Files passed: {files_passed}")
    print(f"📁 Files failed: {files_failed}")
    print(f"🧪 Total tests: {total_tests_run}")
    print(f"✅ Tests passed: {total_tests_passed}")
    print(f"❌ Tests failed: {total_tests_failed}")
    print(f"⏭️  Tests skipped: {total_tests_skipped}")
    
    if total_tests_failed == 0 and files_failed == 0:
        print("🎉 ALL UNIT TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {total_tests_failed} unit test(s) failed across {files_failed} file(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the unit test suite
python run_unit_tests_detailed.py
exit_code=$?

# Clean up
rm -f run_unit_tests_detailed.py

# Exit with the same code as the test runner
exit $exit_code