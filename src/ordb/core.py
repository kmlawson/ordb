"""Core search engine for ordb."""

import sqlite3
import sys
import re
import gzip
import urllib.request
import urllib.error
from pathlib import Path
from difflib import SequenceMatcher
from .config import apply_character_replacement


def download_database(url, db_path):
    """Download and decompress the database from the given URL."""
    from .config import Colors
    
    print(f"{Colors.BRIGHT}Downloading dictionary database from:")
    print(f"{url}{Colors.END}")
    print()
    
    try:
        # Create user data directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download compressed database
        temp_gz_path = db_path.with_suffix('.db.gz')
        
        print("Downloading compressed database...")
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(temp_gz_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}% ({downloaded // 1024} KB / {total_size // 1024} KB)", end='', flush=True)
        
        print(f"\n{Colors.SUCCESS}Download complete!{Colors.END}")
        
        # Decompress the database
        print("Decompressing database...")
        with gzip.open(temp_gz_path, 'rb') as gz_file:
            with open(db_path, 'wb') as db_file:
                db_file.write(gz_file.read())
        
        # Clean up compressed file
        temp_gz_path.unlink()
        
        print(f"{Colors.SUCCESS}Database ready at: {db_path}{Colors.END}")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"{Colors.ERROR}HTTP Error {e.code}: {e.reason}{Colors.END}")
        return False
    except urllib.error.URLError as e:
        print(f"{Colors.ERROR}URL Error: {e.reason}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.ERROR}Error downloading database: {e}{Colors.END}")
        return False


def extract_bundled_database():
    """Extract the bundled compressed database to user directory."""
    from .config import Colors
    import io
    import os
    
    user_db_path = Path.home() / '.ordb' / 'articles.db'
    
    try:
        # Try to find bundled database - look for it relative to package installation
        bundled_db_data = None
        
        # Method 1: Try to find it via importlib.resources (for proper wheel installs)
        try:
            from importlib.resources import files
            # Look for the database file in the package root (not in src/ordb)
            import ordb
            package_root = Path(ordb.__file__).parent.parent.parent
            bundled_db_path = package_root / 'db' / 'articles.db.gz'
            if bundled_db_path.exists():
                bundled_db_data = bundled_db_path.read_bytes()
        except Exception:
            pass
        
        # Method 2: Try to read from package data if included via MANIFEST.in
        if bundled_db_data is None:
            try:
                import pkg_resources
                bundled_db_data = pkg_resources.resource_string('ordb', '../db/articles.db.gz')
            except Exception:
                pass
        
        # Method 3: Look relative to the current package location
        if bundled_db_data is None:
            try:
                import ordb
                package_dir = Path(ordb.__file__).parent
                possible_paths = [
                    package_dir / '../db/articles.db.gz',  # Development layout
                    package_dir / 'db/articles.db.gz',    # If moved to package
                    package_dir / '../../db/articles.db.gz'  # Another possible layout
                ]
                for path in possible_paths:
                    abs_path = path.resolve()
                    if abs_path.exists():
                        bundled_db_data = abs_path.read_bytes()
                        break
            except Exception:
                pass
        
        if bundled_db_data is None:
            # No bundled database found
            return None
        
        print(f"{Colors.BRIGHT}Setting up ordb dictionary database...{Colors.END}")
        print()
        print(f"{Colors.WARNING}⚠️  This will extract a large dictionary database to ~/.ordb/{Colors.END}")
        print(f"   • Compressed size: ~21 MB")
        print(f"   • Uncompressed size: ~90 MB")
        print(f"   • Contains 90,000+ Norwegian dictionary entries")
        print()
        
        response = input("Continue with database setup? [Y/n]: ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("Database setup cancelled.")
            return None
        
        # Create user data directory
        user_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        print("Extracting database... (this may take a moment)")
        
        # Decompress and save
        with gzip.open(io.BytesIO(bundled_db_data), 'rb') as gz_file:
            with open(user_db_path, 'wb') as db_file:
                # Write in chunks to show progress for large file
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = gz_file.read(chunk_size)
                    if not chunk:
                        break
                    db_file.write(chunk)
                    print(".", end="", flush=True)
        
        print()  # New line after progress dots
        print(f"{Colors.SUCCESS}✅ Database ready at: {user_db_path}{Colors.END}")
        return user_db_path
        
    except Exception as e:
        print(f"{Colors.ERROR}Error extracting bundled database: {e}{Colors.END}")
        return None


def setup_database(db_path):
    """Connect to the SQLite database, extracting or downloading if necessary."""
    db_path = Path(db_path)
    
    # If database exists, just connect
    if db_path.exists():
        return sqlite3.connect(db_path)
    
    # Database not found - trigger first-run setup
    from .config import Colors
    
    print(f"{Colors.WARNING}Dictionary database not found at: {db_path}{Colors.END}")
    print()
    
    # First try to extract bundled database
    extracted_path = extract_bundled_database()
    if extracted_path and extracted_path.exists():
        return sqlite3.connect(extracted_path)
    
    # Fallback to downloading
    print()
    print(f"{Colors.WARNING}Bundled database not available. Attempting download...{Colors.END}")
    print("This is a one-time setup that will download about 20-30 MB.")
    print()
    
    # Default GitHub URL - can be overridden
    default_url = "https://github.com/kmlawson/ordb/releases/latest/download/articles.db.gz"
    
    print(f"Download URL: {default_url}")
    print()
    response = input("Press Enter to download, or paste alternative URL: ").strip()
    
    download_url = response if response else default_url
    
    if download_database(download_url, db_path):
        return sqlite3.connect(db_path)
    else:
        print(f"{Colors.ERROR}Failed to download database. Please check your internet connection or try again later.{Colors.END}")
        print()
        print("Alternative method - generate database from source:")
        print("1. Visit https://ord.uib.no/")
        print("2. Click 'Ordlister' and download article.json")
        print("3. Get ordb source: git clone https://github.com/kmlawson/ordb.git")
        print("4. Place article.json in the ordb directory")
        print("5. Run: cd ordb && python db/json-to-db.py")
        print("6. Copy generated articles.db to ~/.ordb/articles.db")
        print()
        print("Note: This requires ~200 MB disk space and may take several minutes")
        sys.exit(1)


def similarity(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def parse_search_query(query):
    """Parse search query to determine search type and clean query."""
    original_query = query
    search_type = 'exact'
    
    # Full text search: %term
    if query.startswith('%'):
        search_type = 'fulltext'
        query = query[1:]
    # Prefix match: term@
    elif query.endswith('@') and not query.startswith('@'):
        search_type = 'prefix'
        query = query[:-1]
    # Match anywhere: @term or @term@
    elif query.startswith('@'):
        search_type = 'anywhere_term'
        query = query[1:]
        if query.endswith('@'):
            query = query[:-1]
    
    return search_type, query, original_query


def search_exact(conn, query, include_expr=True):
    """Search for exact matches in lemmas and inflections."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        # Search in primary lemma
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE lemma = ? COLLATE NOCASE {expr_filter}
        ''', (variant,))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
        
        # Search in all lemmas and inflections for exact matches
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%'))
        
        # Add results, avoiding duplicates
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                # Check if it's actually an exact match (word boundaries)
                all_lemmas = result[2].split(' | ') if result[2] else []
                inflections = result[5].split(' | ') if result[5] else []
                if (variant.lower() in [lemma.lower() for lemma in all_lemmas] or
                    variant.lower() in [infl.lower() for infl in inflections]):
                    results.append(result)
                    seen_ids.add(result[0])
    
    # Sort by: 1) homonym number (NULL treated as 1), 2) word class priority (NOUN first), 3) lemma length
    def sort_key(x):
        homonym = x[8] if x[8] is not None else 1
        word_class_priority = 0 if x[3] == 'NOUN' else 1 if x[3] == 'VERB' else 2 if x[3] == 'ADJ' else 3 if x[3] == 'ADV' else 4
        return (homonym, word_class_priority, len(x[1]))
    
    results.sort(key=sort_key)
    
    # Don't include expressions as separate entries - they will be grouped under main entries
    return results


def search_prefix(conn, query, include_expr=False):
    """Search for terms that start with the query."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (lemma LIKE ? COLLATE NOCASE
            OR all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number = result
                
                # Check if any term actually starts with the variant
                all_lemmas_list = all_lemmas.split(' | ') if all_lemmas else []
                inflections_list = inflections.split(' | ') if inflections else []
                all_terms = [lemma] + all_lemmas_list + inflections_list
                
                if any(term.lower().startswith(variant.lower()) for term in all_terms if term):
                    results.append(result)
                    seen_ids.add(result[0])
    
    # Sort by lemma length (shortest first)
    results.sort(key=lambda x: len(x[1]))
    return results


def search_anywhere_term(conn, query, include_expr=False):
    """Search for terms that contain the query anywhere."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (lemma LIKE ? COLLATE NOCASE
            OR all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length (shortest first)
    results.sort(key=lambda x: len(x[1]))
    return results


def search_fulltext(conn, query, include_expr=False):
    """Search in all content including definitions and examples."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND a.word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT DISTINCT a.article_id, a.lemma, a.all_lemmas, a.word_class, a.gender, a.inflections, a.inflection_table, a.etymology, a.homonym_number
            FROM articles a
            LEFT JOIN definitions d ON a.article_id = d.article_id
            LEFT JOIN examples e ON a.article_id = e.article_id
            WHERE (a.lemma LIKE ? COLLATE NOCASE
            OR a.all_lemmas LIKE ? COLLATE NOCASE
            OR a.inflections LIKE ? COLLATE NOCASE
            OR d.content LIKE ? COLLATE NOCASE 
            OR e.quote LIKE ? COLLATE NOCASE
            OR a.etymology LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length (shortest first)
    results.sort(key=lambda x: len(x[1]))
    return results


def search_fuzzy(conn, query, threshold=0.6, include_expr=False):
    """Search for fuzzy matches."""
    cursor = conn.cursor()
    
    expr_filter = "" if include_expr else "WHERE word_class != 'EXPR'"
    cursor.execute(f'SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number FROM articles {expr_filter}')
    all_articles = cursor.fetchall()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    fuzzy_matches = []
    seen_ids = set()
    
    for variant in query_variants:
        for article in all_articles:
            article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number = article
            
            # Skip if already added
            if article_id in seen_ids:
                continue
            
            # Check similarity with primary lemma
            if similarity(variant, lemma) >= threshold:
                fuzzy_matches.append((article, similarity(variant, lemma)))
                seen_ids.add(article_id)
                continue
            
            # Check similarity with all lemmas
            lemmas = all_lemmas.split(' | ') if all_lemmas else []
            max_similarity = 0
            for lem in lemmas:
                sim = similarity(variant, lem)
                if sim > max_similarity:
                    max_similarity = sim
            
            if max_similarity >= threshold:
                fuzzy_matches.append((article, max_similarity))
                seen_ids.add(article_id)
    
    # Sort by similarity score (descending), then by lemma length (ascending)
    fuzzy_matches.sort(key=lambda x: (-x[1], len(x[0][1])))
    
    return [match[0] for match in fuzzy_matches]


def search_anywhere(conn, query, include_expr=False):
    """Search anywhere in definitions and examples."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND a.word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT DISTINCT a.article_id, a.lemma, a.all_lemmas, a.word_class, a.gender, a.inflections, a.inflection_table, a.etymology, a.homonym_number
            FROM articles a
            LEFT JOIN definitions d ON a.article_id = d.article_id
            LEFT JOIN examples e ON a.article_id = e.article_id
            WHERE (d.content LIKE ? COLLATE NOCASE 
            OR e.quote LIKE ? COLLATE NOCASE
            OR a.all_lemmas LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length (shortest first)
    results.sort(key=lambda x: len(x[1]))
    return results


def search_expressions_only(conn, query):
    """Search only for expressions (word_class = 'EXPR')."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        cursor.execute('''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE word_class = 'EXPR' AND (
                lemma LIKE ? COLLATE NOCASE
                OR all_lemmas LIKE ? COLLATE NOCASE
            )
        ''', (f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length (shortest first)
    results.sort(key=lambda x: len(x[1]))
    return results


def search_all_examples(conn, query):
    """Find all examples across the dictionary that contain the exact target word."""
    cursor = conn.cursor()
    
    # Apply character replacement to the query
    query_variants = apply_character_replacement(query)
    
    all_examples = []
    seen_examples = set()  # To avoid duplicates
    
    for variant in query_variants:
        # Search in regular examples table
        cursor.execute('''
            SELECT DISTINCT e.quote, e.explanation, a.lemma, a.word_class
            FROM examples e
            JOIN articles a ON e.article_id = a.article_id
            WHERE e.quote IS NOT NULL AND e.quote != ''
            AND e.quote LIKE ? COLLATE NOCASE
            ORDER BY a.lemma, e.id
        ''', (f'%{variant}%',))
        
        for quote, explanation, lemma, word_class in cursor.fetchall():
            if quote and quote not in seen_examples:
                # Check if it's actually an exact word match (not part of another word)
                import re
                # Use word boundaries to ensure exact matches
                pattern = r'\\b' + re.escape(variant.lower()) + r'\\b'
                if re.search(pattern, quote.lower()):
                    all_examples.append((quote, explanation, lemma, word_class))
                    seen_examples.add(quote)
                else:
                    # Also try simple space-separated word matching as fallback
                    words = quote.lower().split()
                    if variant.lower() in words:
                        all_examples.append((quote, explanation, lemma, word_class))
                        seen_examples.add(quote)
    
    # Sort by lemma name for organized output
    all_examples.sort(key=lambda x: x[2])  # Sort by lemma
    return all_examples


def get_related_expressions(conn, search_term):
    """Get fixed expressions that are explicitly linked to the search term."""
    cursor = conn.cursor()
    
    # Get expressions that are explicitly linked to this search term via cross-references
    cursor.execute('''
        SELECT DISTINCT a.article_id, a.lemma, d.id as def_id, d.content, e.quote, e.explanation
        FROM expression_links el
        JOIN articles a ON el.expression_article_id = a.article_id
        LEFT JOIN definitions d ON a.article_id = d.article_id
        LEFT JOIN examples e ON d.id = e.definition_id
        WHERE el.target_lemma = ? AND a.word_class = 'EXPR'
        ORDER BY a.lemma, d.order_num, d.id
    ''', (search_term,))
    
    linked_expressions = cursor.fetchall()
    
    # Group by expression lemma and definition
    expr_dict = {}
    for article_id, lemma, def_id, content, quote, explanation in linked_expressions:
        if lemma not in expr_dict:
            expr_dict[lemma] = {'definitions': []}
        
        # Find if this definition already exists
        def_found = False
        for def_data in expr_dict[lemma]['definitions']:
            if def_data['id'] == def_id:
                if quote:
                    def_data['examples'].append((quote, explanation))
                def_found = True
                break
        
        # If definition not found, add it
        if not def_found and content:
            expr_dict[lemma]['definitions'].append({
                'id': def_id,
                'content': content,
                'examples': [(quote, explanation)] if quote else []
            })
    
    return expr_dict


def get_definitions_and_examples(conn, article_id):
    """Get structured definitions and examples for an article."""
    cursor = conn.cursor()
    
    # Get definitions ordered by level and order_num
    cursor.execute('''
        SELECT id, definition_id, parent_id, level, content, order_num
        FROM definitions 
        WHERE article_id = ? 
        ORDER BY level, order_num
    ''', (article_id,))
    definitions = cursor.fetchall()
    
    # Get examples
    cursor.execute('''
        SELECT definition_id, quote, explanation
        FROM examples 
        WHERE article_id = ?
    ''', (article_id,))
    examples = cursor.fetchall()
    
    # Group examples by definition
    examples_by_def = {}
    for def_id, quote, explanation in examples:
        if def_id not in examples_by_def:
            examples_by_def[def_id] = []
        examples_by_def[def_id].append((quote, explanation))
    
    return definitions, examples_by_def