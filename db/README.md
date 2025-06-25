# Database Files

This directory contains the database files and tools for the ordb Norwegian dictionary project.

## Files

### `articles.db.gz` (21 MB compressed)
- **Purpose**: Compressed SQLite database ready for distribution
- **Source**: Generated from `articles.json` using `json-to-db.py`
- **Used when**: Automatically downloaded to `~/.ordb/articles.db` on first run of ordb
- **Contains**: 90,000+ processed Norwegian dictionary entries with optimized search indexes

### `articles.json.gz` (17 MB compressed)  
- **Purpose**: Compressed source data from Norwegian Language Council
- **Source**: Original JSON data from https://ord.uib.no/ 
- **Used when**: Users want to regenerate database with latest data
- **Contains**: Raw dictionary entries in original JSON format (181 MB uncompressed)

### `concepts.json` (24 KB)
- **Purpose**: Abbreviation expansion mappings
- **Source**: Part of the original Norwegian Language Council dataset
- **Used when**: Running `json-to-db.py` to convert JSON to SQLite database
- **Contains**: Mappings like "norr." → "norrønt", "lat." → "latin", etc.

### `json-to-db.py` (27 KB)
- **Purpose**: Converts `articles.json` to optimized SQLite database
- **Usage**: `python json-to-db.py` (requires `articles.json` and `concepts.json`)
- **Output**: Creates `articles.db` with proper indexes and processed content

## Database Regeneration

To regenerate the database with fresh data:

1. **Download latest data**:
   - Visit https://ord.uib.no/
   - Click "Ordlister" 
   - Download `article.json`

2. **Regenerate database**:
   ```bash
   # Place article.json in this directory
   python json-to-db.py
   ```

3. **Compress for distribution**:
   ```bash
   gzip -9 -c articles.db > articles.db.gz
   ```

⚠️ **Warning**: The conversion script has only been tested with data up to the latest release date. Newer versions may require script updates.

## Distribution Strategy

- **PyPI/pip**: Ships lightweight package without database
- **Homebrew**: Uses post-install hook to download database  
- **First run**: Downloads `articles.db.gz` from GitHub releases, decompresses to `~/.ordb/`
- **Offline usage**: Users can manually generate database using files in this directory