# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-06-24

### Added
- Initial release of ordb - Norwegian dictionary search tool
- Fast search through 90,000+ Norwegian Bokmål dictionary entries
- Multiple search modes: exact, fuzzy, prefix, anywhere, full-text, expression-only
- Smart character replacement (aa→å, oe→ø, ae→æ)
- Rich terminal output with colored formatting and pagination
- Line-by-line navigation with j/k keys and arrow keys
- Comprehensive results including definitions, examples, etymology, inflections
- Fixed expressions (faste uttrykk) support
- Word class filtering (noun, verb, adjective, adverb)
- Multiple output modes: full entries, examples-only, etymology-only, inflections-only
- Customizable configuration for colors, limits, and display options
- Statistics view showing comprehensive dictionary coverage
- Modular codebase with clean separation of concerns
- Support for multiple configuration file locations
- Database creation tools and test suite

### Features
- **Search Types**:
  - Exact match with automatic fallback to prefix search
  - Fuzzy matching for typo tolerance
  - Prefix search (`word@`)
  - Anywhere in term search (`@word`)
  - Full-text search (`%word`)
  - Expression-only search (`-x` flag)
  - All-examples search (`--all-examples`)

- **Display Options**:
  - Examples-only view (`--only-examples`)
  - Etymology-only view (`-e`)
  - Inflections-only view (`-i`)
  - Hide definitions (`--no-definitions`)
  - Hide examples (`--no-examples`)

- **Filtering**:
  - By word class: `--noun`, `--verb`, `--adj`, `--adv`
  - Result limits: `--limit N`
  - Example limits: `--max-examples N`

- **Terminal Features**:
  - Colored output with customizable color schemes
  - Pagination with navigation controls
  - Line-by-line scrolling (j/k keys, arrow keys)
  - Terminal size detection and adaptation

- **Configuration**:
  - Color customization for all output elements
  - Search behavior configuration
  - Pagination and display preferences
  - Multiple config file locations support

### Technical
- Modular architecture with 5 core modules:
  - `cli.py` - Command-line interface
  - `core.py` - Search engine
  - `display.py` - Output formatting
  - `config.py` - Configuration management
  - `pagination.py` - Terminal UI
- SQLite database with optimized indexes
- Comprehensive test suite (17 test files)
- Python 3.8+ compatibility
- Zero external dependencies for core functionality

### Database
- 90,841 total dictionary entries
- 111,425 definitions
- 83,849 examples
- 8,218 expressions
- Comprehensive word type classification (98.4% coverage)
- Rich inflection tables and etymology information
