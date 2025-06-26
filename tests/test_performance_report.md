# Test Performance Report

**Last Run:** 2025-06-26 at Thu 26 Jun 2025 11:27:00 CEST

## Test File Performance Summary

| Test File | Tests Count | Duration | Status | Notes |
|-----------|-------------|----------|--------|-------|
| test_all_examples_and_config.py | 8 | 0.606s | ✅ PASS | Fast |
| test_character_replacement.py | 10 | 11.551s | ✅ PASS | Slow - character replacement tests |
| test_compact_inflections.py | 2 | ~0.5s | ✅ PASS | Fast |
| test_comprehensive_functionality.py | 21 | 7.422s | ✅ PASS | Medium - comprehensive feature testing |
| test_config_wizard_completeness.py | 2 | 0.001s | ✅ PASS | Very fast |
| test_database_integrity.py | 13 | 2.029s | ✅ PASS | Medium - database validation |
| test_display_flags.py | 5 | 1.726s | ✅ PASS | Medium |
| test_etymology_flags.py | 2 | 0.842s | ✅ PASS | Fast |
| test_inflection_flags.py | 2 | 0.214s | ✅ PASS | Fast |
| test_interactive_fuzzy_search.py | 21 | 20.666s | ✅ PASS | Slowest - interactive testing with subprocess |
| test_only_examples_expressions.py | 3 | 0.553s | ✅ PASS | Fast |
| test_pagination.py | 9 | 3.556s | ✅ PASS | Medium |
| test_platform_paths.py | 6 | 0.001s | ✅ PASS | Very fast |
| test_word_filters.py | 4 | 0.624s | ✅ PASS | Fast |

## Performance Categories

### Very Fast (< 0.1s)
- test_config_wizard_completeness.py (0.001s)
- test_platform_paths.py (0.001s)

### Fast (0.1s - 1.0s)
- test_all_examples_and_config.py (0.606s)
- test_compact_inflections.py (~0.5s)
- test_etymology_flags.py (0.842s)
- test_inflection_flags.py (0.214s)
- test_only_examples_expressions.py (0.553s)
- test_word_filters.py (0.624s)

### Medium (1.0s - 5.0s)
- test_display_flags.py (1.726s)
- test_database_integrity.py (2.029s)
- test_pagination.py (3.556s)

### Slow (5.0s - 15.0s)
- test_comprehensive_functionality.py (7.422s)
- test_character_replacement.py (11.551s)

### Very Slow (> 15.0s)
- test_interactive_fuzzy_search.py (20.666s) - Interactive testing inherently slow

## Total Test Statistics

- **Total Test Files:** 14
- **Total Tests:** 108 tests
- **Total Runtime:** ~50.3 seconds
- **Success Rate:** 100% (108/108 passing)

## Performance Notes

### Optimizations Applied
- Changed all test commands from `uv run ordb` to `python -m ordb` for faster execution
- Added `--no-paginate` flags to prevent pagination interference
- Simplified database path handling to use standard user locations
- Removed unnecessary environment setup and path manipulation

### Slowest Tests Analysis
1. **test_interactive_fuzzy_search.py (20.7s)** - Slow due to interactive subprocess communication testing
2. **test_character_replacement.py (11.6s)** - Multiple character replacement searches across different modes
3. **test_comprehensive_functionality.py (7.4s)** - Tests all major features and command-line flags

### Performance Improvements Achieved
- test_comprehensive_functionality.py: 21.1s → 7.4s (65% faster)
- test_character_replacement.py: 10.6s → 11.6s (slight regression, but within variance)
- test_word_filters.py: From timeout → 0.6s (completely fixed)

## Recommendations

- Interactive tests (test_interactive_fuzzy_search.py) are inherently slow but necessary for UI testing
- Character replacement tests could potentially be optimized by reducing test query diversity
- All other tests perform within acceptable ranges for their functionality coverage

**Report Generated:** Thu 26 Jun 2025 11:27:00 CEST