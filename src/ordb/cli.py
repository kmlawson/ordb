"""Command-line interface for ordb."""

import argparse
import sys
from .config import Colors, search_config
from .core import (
    setup_database, parse_search_query, search_exact, search_fuzzy, 
    search_prefix, search_anywhere_term, search_fulltext, search_anywhere,
    search_expressions_only, search_all_examples
)
from .pagination import paginate_output


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ordb - Norwegian dictionary search tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''\
{Colors.BOLD}Examples:{Colors.END}
  %(prog)s gå                   # Exact match for "gå" (fallback to prefix if no exact match)
  %(prog)s -f huse              # Fuzzy match: finds "hus" even with typos/misspellings
  %(prog)s -a "til fots"        # Search anywhere for "til fots"
  %(prog)s -x hus               # Search only expressions containing "hus"
  %(prog)s --only-examples hus  # Show only examples for "hus"
  %(prog)s -e hus               # Show only etymology for "hus"
  %(prog)s -i hus               # Show only inflections for "hus"
  %(prog)s --adj stor           # Find only adjectives matching "stor"
  %(prog)s --verb gå            # Find only verbs matching "gå"
  %(prog)s --noun hus           # Find only nouns matching "hus"
  %(prog)s --adv fort           # Find only adverbs matching "fort"
  %(prog)s -s                   # Show comprehensive dictionary statistics

{Colors.BOLD}Special Search Syntax:{Colors.END}
  %(prog)s ære@                 # Prefix: terms starting with "ære" (ære, æresdrap, etc.)
  %(prog)s @ære                 # Anywhere in term: terms containing "ære" (ære, lærebok, etc.)
  %(prog)s @ære@                # Same as @ære
  %(prog)s %%nasjonal           # Full-text: search all content for "nasjonal"

{Colors.BOLD}Character Replacement:{Colors.END}
  %(prog)s gaar                 # Automatically tries "gå" (aa→å replacement)
  %(prog)s hoer                 # Automatically tries "hør" (oe→ø replacement)
  %(prog)s laere                # Automatically tries "lære" (ae→æ replacement)

{Colors.BOLD}Configuration:{Colors.END}
  Colors, character replacement, and default limits can be customized.
  Use -c flag to launch configuration wizard.

{Colors.BOLD}Auto-fallback:{Colors.END}
  If no exact matches are found, automatically tries prefix search.
        '''
    )
    
    parser.add_argument('query', nargs='?', help='Search term')
    parser.add_argument('-f', '--fuzzy', action='store_true', 
                       help='Enable fuzzy matching (finds similar words despite typos/misspellings)')
    parser.add_argument('-a', '--anywhere', action='store_true',
                       help='Search anywhere in definitions and examples')
    parser.add_argument('-x', '--expressions-only', action='store_true',
                       help='Search only expressions ([expr] word class)')
    parser.add_argument('-t', '--threshold', type=float, default=0.6,
                       help='Similarity threshold for fuzzy matching (0.0-1.0, default: 0.6)')
    parser.add_argument('--no-definitions', action='store_true',
                       help='Hide definitions in output')
    parser.add_argument('--no-examples', action='store_true',
                       help='Hide examples in output')
    parser.add_argument('--only-examples', action='store_true',
                       help='Show only examples (including faste uttrykk examples)')
    parser.add_argument('--all-examples', action='store_true',
                       help='Find exact matches of target word in all examples across dictionary')
    parser.add_argument('-e', '--only-etymology', action='store_true',
                       help='Show only etymology for hits')
    parser.add_argument('-i', '--only-inflections', action='store_true',
                       help='Show only inflections, with each category on separate line')
    parser.add_argument('--adj', action='store_true',
                       help='Return only hits of word type [adj]')
    parser.add_argument('--verb', action='store_true',
                       help='Return only hits of word type [verb]')
    parser.add_argument('--noun', action='store_true',
                       help='Return only hits of word type [noun]')
    parser.add_argument('--adv', action='store_true',
                       help='Return only hits of word type [adv]')
    parser.add_argument('--max-examples', type=int, default=None,
                       help='Maximum examples per definition (default: show all)')
    parser.add_argument('--limit', type=int, default=search_config.default_limit,
                       help=f'Maximum number of results to show (default: {search_config.default_limit})')
    parser.add_argument('--db', default=os.path.expanduser('~/.ordb/articles.db'),
                       help='Database file path (default: ~/.ordb/articles.db)')
    parser.add_argument('--test', action='store_true',
                       help='Run test searches with predefined words')
    parser.add_argument('-s', '--stats', action='store_true',
                       help='Show comprehensive dictionary statistics')
    parser.add_argument('-p', '--paginate', action='store_true',
                       help='Force pagination even when config pagination=False')
    parser.add_argument('-P', '--no-paginate', action='store_true',
                       help='Force pagination off even when config pagination=True')
    parser.add_argument('-c', '--config', action='store_true',
                       help='Launch interactive configuration wizard')
    
    args = parser.parse_args()
    
    # Handle config wizard
    if args.config:
        try:
            import subprocess
            subprocess.run([sys.executable, 'config-wizard.py'])
            return
        except Exception as e:
            print(f"{Colors.ERROR}Error launching configuration wizard: {e}{Colors.END}")
            sys.exit(1)
    
    # Validate arguments
    if not args.test and not args.query and not args.stats:
        print(f"{Colors.ERROR}Error: Either provide a search term, use --test flag, --stats flag, or --config flag{Colors.END}")
        sys.exit(1)
    
    if not 0.0 <= args.threshold <= 1.0:
        print(f"{Colors.ERROR}Error: Threshold must be between 0.0 and 1.0{Colors.END}")
        sys.exit(1)
    
    # Adjust limit when pagination is enabled and user didn't specify custom limit
    if (search_config.pagination or args.paginate) and args.limit == search_config.default_limit:
        args.limit = search_config.limit_with_pagination
    
    # Connect to database
    conn = setup_database(args.db)
    
    # Handle test mode
    if args.test:
        from .display import run_test_searches
        run_test_searches(conn, args)
        return
    
    # Handle statistics mode
    if args.stats:
        from .display import display_statistics
        display_statistics(conn)
        conn.close()
        return
    
    try:
        # Parse search query for special syntax
        search_type, clean_query, original_query = parse_search_query(args.query)
        
        # Override with command line flags if present
        if args.all_examples:
            # Special case: search all examples across dictionary
            print(f"{Colors.HEADER}🔍 Searching all examples for exact matches of '{Colors.BOLD}{args.query}{Colors.END}{Colors.HEADER}'{Colors.END}")
            examples = search_all_examples(conn, args.query)
            
            if not examples:
                print(f"{Colors.WARNING}No examples found containing '{args.query}'.{Colors.END}")
                return
            
            # Collect all output for pagination
            output_parts = []
            output_parts.append(f"\n{Colors.BOLD}Found {len(examples)} example(s) containing '{args.query}':{Colors.END}")
            output_parts.append(f"{Colors.INFO}{'=' * 80}{Colors.END}")
            
            # Display examples in semicolon-separated format
            example_texts = []
            for quote, explanation, lemma, word_class in examples[:args.limit]:
                from .display import highlight_search_term
                highlighted_quote = highlight_search_term(quote, args.query, Colors.EXAMPLE)
                example_text = highlighted_quote
                if explanation:
                    example_text += f" ({explanation})"
                example_texts.append(example_text)
            
            if example_texts:
                output_parts.append(f"  {'; '.join(example_texts)}")
            
            if len(examples) > args.limit:
                output_parts.append(f"{Colors.INFO}... and {len(examples) - args.limit} more example(s){Colors.END}")
                output_parts.append(f"{Colors.INFO}Use --limit {len(examples)} to see all examples{Colors.END}")
            
            # Join all output and paginate
            full_output = '\n'.join(output_parts)
            paginate_output(full_output, force_pagination=args.paginate, disable_pagination=args.no_paginate)
            
            return
        elif args.expressions_only:
            search_type = 'expressions_only'
            clean_query = args.query
        elif args.fuzzy:
            search_type = 'fuzzy'
            clean_query = args.query
        elif args.anywhere:
            search_type = 'anywhere'
            clean_query = args.query
        
        # Perform search based on type
        if search_type == 'expressions_only':
            results = search_expressions_only(conn, clean_query)
        elif search_type == 'fuzzy':
            results = search_fuzzy(conn, clean_query, args.threshold, include_expr=False)
        elif search_type == 'anywhere':
            results = search_anywhere(conn, clean_query, include_expr=False)
        elif search_type == 'prefix':
            results = search_prefix(conn, clean_query, include_expr=False)
        elif search_type == 'anywhere_term':
            results = search_anywhere_term(conn, clean_query, include_expr=False)
        elif search_type == 'fulltext':
            results = search_fulltext(conn, clean_query, include_expr=False)
        else:
            results = search_exact(conn, clean_query, include_expr=True)
            
            # If no exact matches found, fallback to prefix search
            if not results and search_type == 'exact':
                results = search_prefix(conn, clean_query, include_expr=True)
        
        # Apply word class filtering if specified before displaying count
        if args.adj:
            results = [result for result in results if result[3] and 'ADJ' in result[3]]
        elif args.verb:
            results = [result for result in results if result[3] and 'VERB' in result[3]]
        elif args.noun:
            results = [result for result in results if result[3] and 'NOUN' in result[3]]
        elif args.adv:
            results = [result for result in results if result[3] and 'ADV' in result[3]]
        
        # Display results
        if not results:
            print(f"{Colors.WARNING}No results found.{Colors.END}")
            return
        
        # Display results using the display module
        from .display import format_result
        
        # Handle display flags
        if args.only_examples:
            show_definitions = False
            show_examples = True
            only_examples = True
            only_etymology = False
            only_inflections = False
        elif args.only_etymology:
            show_definitions = False
            show_examples = False
            only_examples = False
            only_etymology = True
            only_inflections = False
        elif args.only_inflections:
            show_definitions = False
            show_examples = False
            only_examples = False
            only_etymology = False
            only_inflections = True
        else:
            show_definitions = not args.no_definitions
            show_examples = not args.no_examples
            only_examples = False
            only_etymology = False
            only_inflections = False
        
        # Collect all output for pagination
        output_parts = []
        
        # Add search header
        if search_type == 'expressions_only':
            output_parts.append(f"{Colors.HEADER}🔍 Expression search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (expressions only){Colors.END}")
        elif search_type == 'fuzzy':
            output_parts.append(f"{Colors.HEADER}🔍 Fuzzy search for '~{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (threshold: {args.threshold}){Colors.END}")
        elif search_type == 'anywhere':
            output_parts.append(f"{Colors.HEADER}🔍 Searching anywhere for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}'{Colors.END}")
        elif search_type == 'prefix':
            output_parts.append(f"{Colors.HEADER}🔍 Prefix search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}@' (terms starting with '{clean_query}'){Colors.END}")
        elif search_type == 'anywhere_term':
            output_parts.append(f"{Colors.HEADER}🔍 Term search for '@{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (terms containing '{clean_query}'){Colors.END}")
        elif search_type == 'fulltext':
            output_parts.append(f"{Colors.HEADER}🔍 Full-text search for '%{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (all content){Colors.END}")
        else:
            output_parts.append(f"{Colors.HEADER}🔍 Exact search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}'{Colors.END}")
        
        # Format results
        for i, result in enumerate(results[:args.limit]):
            show_expressions = (i == 0)  # Show expressions only for first result
            result_output = format_result(conn, result, show_definitions, show_examples, args.max_examples, clean_query, show_expressions, only_examples, only_etymology, only_inflections)
            output_parts.append(result_output)
            if i < min(len(results), args.limit) - 1:
                output_parts.append(f"{Colors.INFO}{'-' * 80}{Colors.END}")
        
        # Add result count if more than 1 result
        if len(results) > 1:
            if len(results) > args.limit:
                output_parts.append(f"\n{Colors.INFO}Found {len(results)} results (showing {args.limit}). Use --limit {len(results)} to see all.{Colors.END}")
            else:
                output_parts.append(f"\n{Colors.INFO}Found {len(results)} results.{Colors.END}")
        
        # Join all output and paginate
        full_output = '\n'.join(output_parts)
        paginate_output(full_output, force_pagination=args.paginate, disable_pagination=args.no_paginate)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Search interrupted.{Colors.END}")
    except Exception as e:
        print(f"{Colors.ERROR}Error: {e}{Colors.END}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()