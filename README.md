# ordb - Norwegian Dictionary Search Tool

A fast, feature-rich command-line tool for searching an extensive Norwegian bokmål dictionary. Built for linguists, language learners, translators, and anyone working with bokmål text using open source ordbokene.no dictionary data.

## Features

- **Multiple search modes**: exact, fuzzy, prefix, anywhere, full-text, and expression-only
- **Interactive search lists**: fuzzy, prefix, and anywhere searches now show lettered selection menus
- **Smart character replacement**: automatically converts `aa→å`, `oe→ø`, `ae→æ`
- **Rich terminal output** with colored formatting and pagination
- **Comprehensive results** including definitions, examples, etymology, inflections, and fixed expressions
- **Flexible filtering** by word class (noun, verb, adjective, adverb)
- **Cross-platform support**: Windows, macOS, and Linux with platform-appropriate file paths
- **Customizable configuration** for colors, limits, and display options with user friendly configuration wizard
- **Multiple output modes**: full entries, examples-only, etymology-only, inflections-only

## Installation


### Using uv (recommended)
```bash
uv tool install ordb
```

### Using pip
```bash
pip install ordb
```

## Quick Start

```bash
# Search for a word
ordb nord

# Interactive fuzzy search (shows lettered list, press letter key for immediate selection)
ordb -f hus

# Search anywhere in definitions and examples
ordb -a "til fots"

# Show only examples
ordb --only-examples hus

# Search only expressions
ordb -x "hele sitt hjerte"

# Show dictionary statistics
ordb --stats
```

## Search Modes

### Basic Search
```bash
ordb word           # Exact match with fallback to fuzzy search or prefex search (configurable)
```

### Special Search Syntax
```bash
ordb word@          # Prefix: words starting with "word" (interactive selection by default)
ordb @word          # Anywhere in term: terms containing "word" (interactive selection by default)
ordb %word          # Full-text: search all content for "word"
```

### Advanced Search Options
```bash
ordb -f word        # Interactive fuzzy search with lettered list
ordb -a "phrase"    # Search anywhere in definitions/examples
ordb -x expression  # Search only fixed expressions
ordb --all-examples word  # Find word in all examples across dictionary
```

### Overriding Interactive Lists
```bash
ordb -l 5 hus@      # Show 5 prefix results directly (no interactive menu)
ordb -P hus@        # Disable interactive lists and pagination
ordb --limit 10 -f word  # Show 10 fuzzy results directly without pagination
```

### Word Class Filtering
```bash
ordb --noun hus     # Find only nouns matching "hus"
ordb --verb gå      # Find only verbs matching "gå"
ordb --adj stor     # Find only adjectives matching "stor"
ordb --adv fort     # Find only adverbs matching "fort"
```

## Output Modes

### Standard Output
Shows complete entries with definitions, examples, etymology, inflections, and related expressions.

### Specialized Views
```bash
ordb --only-examples word    # Examples only (semicolon-separated)
ordb -e word                # Etymology only
ordb -i word                # Inflections only (multiline format)
ordb --no-definitions word  # Hide definitions
ordb --no-examples word     # Hide examples
```

## Configuration

ordb uses a configuration file to customize colors, search behavior, and display options. The configuration is automatically created when you run the script the first time with a series of defaults but you can easily update this using the interactive configuration wizard:

```bash
ordb -c
```

### Configuration Locations
ordb looks for configuration files in platform-appropriate locations:
- **Unix/Linux/macOS**: `~/.ordb/config` for settings and database
- **Windows**: `%APPDATA%\ordb\config` for settings, `%LOCALAPPDATA%\ordb\` for database

### Key Configuration Options

#### Colors
Customize terminal colors for different elements:
- `lemma` - Main word entries
- `word_class` - Word type labels ([noun], [verb], etc.)
- `definition` - Definition text
- `example` - Example sentences
- `etymology` - Etymology information
- `masculine/feminine/neuter` - Gender colors

#### Search Settings
- `character_replacement` - Enable/disable aa→å, oe→ø, ae→æ conversion
- `default_limit` - Maximum results to show
- `pagination` - Enable/disable pagination
- `page_size` - Lines per page (0 = auto-detect)
- `limit_with_pagination` - Max results with pagination (0 = no limit)
- `show_inflections` - Show/hide inflection tables (default: True)
- `show_etymology` - Show/hide etymology information (default: True)
- `interactive_results_limit` - Maximum results in interactive lists (default: 15)
- `fallback_to_fuzzy` - Use fuzzy search when no exact matches (default: True)
- `interactive_anywhere_search` - Use interactive menus for @ searches (default: True)

**Note**: Interactive lists can be overridden with `-l/--limit` (shows results directly) or `-P` (disables both interactive lists and pagination).

## Examples

### Basic Word Lookup
```bash
$ ordb nord
🔍 Exact search for 'nord'
📖 nord [noun] (neuter)

  1. himmelretning som ligger motsatt retningen mot sola midt på dagen; mots sør, syd
      "vinden stod fra nord"; "det klarner i nord"; "finne nord ved hjelp av kompasset"; "Frankrike grenser til Belgia i nord"
  2. landområde eller stat som ligger i nordlig retning
      "i det høye nord"
  3. i bridge: spiller som har sør, syd som makker
      "nord melder 2 kløver"
  Etymology: norr. norðr | av nord

  Faste uttrykk:
    • nord og ned
      til helvete; svært dårlig
        det går nord og ned og ned med alt
        dømme noen nord og ned og ned
--------------------------------------------------------------------------------
📖 nord (2) [adv]

  1. i nord; i den nordlige delen av et område; på nordsiden; mot nord, i nordlig retning
      "byen ligger nord for sjøen"; "dra nord i landet"
  Etymology: norr. norðr | jamfør nordre og nørdst


Found 2 results.
```

### Interactive Fuzzy Search
```bash
$ ordb -f huse
🔍 Fuzzy search for '~huse' (threshold: 0.6)
Found 15 similar matches (showing first 15):

  a) huse [verb]
  b) hus [noun] (neuter)
  c) huser [noun] (masculine)
  d) husere [verb]
  e) house [noun]
  ...
  o) husgud [noun]
  0) ...more results (25 additional matches)

Press a letter to view the entry, 0 or spacebar for more results, or Enter to cancel: a
📖 huse [verb]
  1. gi ly til; ha som beboer...
```

### Examples Only
```bash
$ ordb --only-examples gå
📖 gå [verb]
  "gå ærend"; "gå en tur"; "gå til fots"; "gå på ski"; "gå i søvne"
```

### Character Replacement
```bash
$ ordb gaar    # Automatically searches for "gå"
$ ordb hoer    # Automatically searches for "hør"  
$ ordb laere   # Automatically searches for "lære"
```

## Database

The dictionary database (`articles.db`) contains:
- **90,841 total entries**
- **111,425 definitions**
- **83,849 examples**
- **8,218 expressions**

Coverage includes:
- 98.4% of entries have identified word types
- Comprehensive inflection tables for verbs, nouns, and adjectives
- Rich etymology information
- Extensive example sentences from real usage

## Development

### Agentic Coding

This tool was built entirely with Claude Code (1.0.35, in June 2025) with Konrad M. Lawson at the prompt. 

### Project Structure
```
ordb/
├── src/ordb/
│   ├── __init__.py      # Package initialization
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   ├── core.py         # Search engine with interactive modes
│   ├── display.py      # Output formatting
│   ├── pagination.py   # Terminal UI and navigation
│   └── utils.py        # Shared utility functions
├── db/
│   ├── json-to-db.py   # Database creation script
│   └── irregular_verbs.json  # Norwegian irregular verb database
├── tests/              # Comprehensive test suite (14 test files)
├── config-wizard.py    # Interactive configuration wizard
└── CHANGELOG.md        # Version history
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_search.py
```

### Building Database
```bash
# Create database from JSON source
python db/json-to-db.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details, including details of the separate license for the ordbokene.no dictionary database.

## Acknowledgments

- Dictionary data from the Norwegian Language Council (Språkrådet). Search their wonderful online dictionaries here: https://ordbokene.no/ and see their downloadable data here: https://ord.uib.no/
- Built with Python 3.8+ for maximum compatibility
- Terminal interface inspired by traditional Unix tools like `less` and `man`

## Support

- **Documentation**: Use -h | --help or read the [README.md](https://github.com/kmlawson/ordb/blob/main/README.md)
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/kmlawson/ordb/issues)

---

**ordb** - Norwegian bokmål dictionary search tool
