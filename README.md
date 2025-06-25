# ordb - Norwegian Dictionary Search Tool

A fast, feature-rich command-line tool for searching the comprehensive Norwegian Bokmål dictionary. Built for linguists, language learners, translators, and anyone working with Norwegian text.

## Features

- **Lightning-fast search** through 90,000+ Norwegian dictionary entries
- **Multiple search modes**: exact, fuzzy, prefix, anywhere, full-text, and expression-only
- **Smart character replacement**: automatically converts `aa→å`, `oe→ø`, `ae→æ`
- **Rich terminal output** with colored formatting and pagination
- **Comprehensive results** including definitions, examples, etymology, inflections, and fixed expressions
- **Flexible filtering** by word class (noun, verb, adjective, adverb)
- **Customizable configuration** for colors, limits, and display options
- **Multiple output modes**: full entries, examples-only, etymology-only, inflections-only

## Installation

### Using pip
```bash
pip install ordb
```

### Using uv (recommended)
```bash
uv tool install ordb
```

### From source
```bash
git clone https://github.com/kmlawson/ordb.git
cd ordb
uv tool install --editable .
```

## Quick Start

```bash
# Search for a word
ordb gå

# Fuzzy search (finds similar words despite typos)
ordb -f huse

# Search anywhere in definitions and examples
ordb -a "til fots"

# Show only examples
ordb --only-examples hus

# Search only expressions
ordb -x "ikke huske"

# Show dictionary statistics
ordb --stats
```

## Search Modes

### Basic Search
```bash
ordb word           # Exact match with fallback to prefix search
```

### Special Search Syntax
```bash
ordb word@          # Prefix: words starting with "word"
ordb @word          # Anywhere in term: terms containing "word"
ordb %word          # Full-text: search all content for "word"
```

### Advanced Search Options
```bash
ordb -f word        # Fuzzy matching (typo-tolerant)
ordb -a "phrase"    # Search anywhere in definitions/examples
ordb -x expression  # Search only fixed expressions
ordb --all-examples word  # Find word in all examples across dictionary
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

ordb uses a configuration file to customize colors, search behavior, and display options. The configuration is automatically created when you run the configuration wizard:

```bash
ordb -c
```

### Configuration Locations
ordb looks for configuration files in this order:
1. `~/.config/ordb/config` (preferred)
2. `~/.config-ordb` 
3. `.config-bm` (legacy)

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
- `show_inflections` - Show/hide inflection tables
- `show_etymology` - Show/hide etymology information

## Examples

### Basic Word Lookup
```bash
$ ordb hus
🔍 Exact search for 'hus'
📖 hus [noun] (neuter)

  Alternative forms: huse

  1. bygning som er oppført for at mennesker eller dyr skal ha et sted å være, bo eller oppholde seg
     "et stort hus"; "bygge hus"; "huset vårt"
  2. familie, slekt, dynasti
     "kongelige hus"; "huset Habsburg"

  Etymology: norrønt hús

  Inflections: Singular: hus, huse Plural: hus, husa, husene

  Faste uttrykk:
    • på huset
      gratis; for husets regning
        "øl på huset"
```

### Fuzzy Search
```bash
$ ordb -f huse
🔍 Fuzzy search for '~huse' (threshold: 0.6)
📖 hus [noun] (neuter)
📖 huse [verb]
📖 huser [noun] (masculine)
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

## Performance

ordb is optimized for speed:
- **SQLite database** with indexed searches
- **Efficient pagination** for large result sets
- **Smart caching** of configuration and colors
- **Minimal memory footprint** even with large datasets

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

### Project Structure
```
ordb/
├── src/ordb/
│   ├── __init__.py      # Package initialization
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   ├── core.py         # Search engine
│   ├── display.py      # Output formatting
│   └── pagination.py   # Terminal UI
├── db/
│   └── json-to-db.py   # Database creation script
├── tests/              # Test suite
└── old/                # Legacy scripts
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

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution
- Additional search algorithms
- Performance optimizations
- New output formats
- Extended configuration options
- Documentation improvements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Dictionary data from the Norwegian Language Council (Språkrådet)
- Built with Python 3.8+ for maximum compatibility
- Terminal interface inspired by traditional Unix tools like `less` and `man`

## Support

- **Documentation**: Full documentation available at [docs.ordb.no](https://docs.ordb.no)
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/ordb/issues)
- **Discussions**: Join the community on [GitHub Discussions](https://github.com/yourusername/ordb/discussions)

---

**ordb** - Making Norwegian dictionary search fast, comprehensive, and enjoyable from the command line.