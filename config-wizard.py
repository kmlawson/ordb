#!/usr/bin/env python3
"""
Interactive configuration wizard for Norwegian dictionary search (ordb).
This wizard helps users configure their .config-bm file settings.
"""

import os
import sys
import configparser
from pathlib import Path

# Color codes for the wizard interface
class WizardColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    GRAY = '\033[90m'

def load_current_config():
    """Load the current configuration file."""
    config_path = Path('.config-bm')
    config = configparser.ConfigParser()
    
    if config_path.exists():
        config.read(config_path)
    
    return config

def get_color_code(color_name):
    """Convert color name to ANSI code."""
    color_map = {
        'DEFAULT': '',
        'BLACK': '\033[30m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'PURPLE': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'GRAY': '\033[90m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'BOLD_RED': '\033[1m\033[91m',
        'BOLD_GREEN': '\033[1m\033[92m',
        'BOLD_YELLOW': '\033[1m\033[93m',
        'BOLD_BLUE': '\033[1m\033[94m',
        'BOLD_PURPLE': '\033[1m\033[95m',
        'BOLD_CYAN': '\033[1m\033[96m',
        'UNDERLINE_RED': '\033[4m\033[91m',
        'UNDERLINE_GREEN': '\033[4m\033[92m',
        'UNDERLINE_BLUE': '\033[4m\033[94m',
    }
    return color_map.get(color_name, '')

def get_user_input(prompt, current_value, options=None, value_type=str, description=None, example_text=None):
    """Get user input with current value as default."""
    
    current_display = current_value if current_value is not None else "not set"
    
    # For color settings, show example in the actual color
    if example_text and options:  # This is a color setting
        color_code = get_color_code(current_value)
        print(f"{WizardColors.CYAN}  Options: {', '.join(options)}{WizardColors.END}")
        user_input = input(f"Color for {prompt}, e.g., {color_code}{example_text}{WizardColors.END} [{WizardColors.YELLOW}{current_display}{WizardColors.END}]: ").strip()
    else:
        # Show description if provided
        if description:
            print(f"{WizardColors.GRAY}  {description}{WizardColors.END}")
        
        # Show options if provided
        if options:
            print(f"{WizardColors.CYAN}  Options: {', '.join(options)}{WizardColors.END}")
        
        print(f"{WizardColors.YELLOW}  Current: {current_display}{WizardColors.END}")
        user_input = input(f"{prompt} [{current_display}]: ").strip()
    
    # Return current value if user just pressed enter
    if not user_input:
        return current_value
    
    # Convert to appropriate type
    if value_type == bool:
        return user_input.lower() in ('true', 'yes', 'y', '1', 'on')
    elif value_type == int:
        try:
            return int(user_input)
        except ValueError:
            print(f"{WizardColors.RED}Invalid number. Using current value.{WizardColors.END}")
            return current_value
    else:
        return user_input

def configure_colors(config):
    """Configure color settings."""
    print(f"\n{WizardColors.HEADER}{WizardColors.BOLD}🎨 Color Configuration{WizardColors.END}")
    print("Configure colors for different elements in search output.")
    
    if 'colors' not in config:
        config.add_section('colors')
    
    colors_section = config['colors']
    
    # Available color options
    color_options = ['DEFAULT (no color)', 'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'PURPLE', 'CYAN', 'WHITE', 'GRAY', 'BOLD', 'UNDERLINE']
    
    color_settings = [
        ('header', '🔍 Exact search for...', 'PURPLE'),
        ('lemma', 'hus', 'CYAN'),
        ('word_class', '[noun]', 'YELLOW'),
        ('masculine', '(masculine)', 'BLUE'),
        ('feminine', '(feminine)', 'RED'),
        ('neuter', '(neuter)', 'GREEN'),
        ('definition', 'bygning med tak og vegger', 'DEFAULT'),
        ('example', '"bygge hus"', 'CYAN'),
        ('highlight', 'hus', 'GREEN'),
        ('etymology', 'Etymology: norr. hús', 'GRAY'),
        ('inflection_label', 'Singular:', 'GRAY'),
        ('error', 'Error: No results found', 'RED'),
        ('warning', 'Warning: No exact matches', 'YELLOW'),
        ('info', '--- Found 2 results ---', 'GRAY'),
        ('success', '✓ Configuration saved', 'GREEN'),
    ]
    
    for setting, example, default in color_settings:
        current = colors_section.get(setting, default)
        # Strip any comments from the current value
        if current and '#' in current:
            current = current.split('#')[0].strip()
        
        # Display "DEFAULT (no color)" for better clarity
        display_current = 'DEFAULT (no color)' if current == 'DEFAULT' else current
        
        print(f"\n{WizardColors.BOLD}{setting.replace('_', ' ').title()}:{WizardColors.END}")
        new_value = get_user_input(
            setting,
            display_current,
            color_options,
            str,
            None,  # No description needed
            example  # Show example text in the actual color
        )
        # Handle "DEFAULT (no color)" input
        if new_value == 'DEFAULT (no color)':
            new_value = 'DEFAULT'
        colors_section[setting] = new_value

def configure_search(config):
    """Configure search settings."""
    print(f"\n{WizardColors.HEADER}{WizardColors.BOLD}🔍 Search Configuration{WizardColors.END}")
    print("Configure search behavior and display options.")
    
    if 'search' not in config:
        config.add_section('search')
    
    search_section = config['search']
    
    search_settings = [
        ('character_replacement', 'Automatically replace aa→å, oe→ø, ae→æ in searches', True, bool, ['True', 'False']),
        ('default_limit', 'Maximum number of results to show by default', 50, int, None),
        ('show_inflections', 'Show inflection tables in output by default', True, bool, ['True', 'False']),
        ('show_etymology', 'Show etymology information in output by default', True, bool, ['True', 'False']),
        ('pagination', 'Enable pagination like "more" command', True, bool, ['True', 'False']),
        ('page_size', 'Number of lines per page (0 = auto-detect from terminal size)', 0, int, None),
        ('limit_with_pagination', 'Max results when pagination is enabled', 500, int, None),
        ('clear_screen', 'Clear screen between pages (set to False if your terminal has issues)', True, bool, ['True', 'False']),
    ]
    
    for setting, description, default, value_type, options in search_settings:
        current = search_section.get(setting)
        if current is None:
            current = default
        elif value_type == bool:
            # Strip comments before parsing boolean
            raw_value = search_section.get(setting, str(default))
            if '#' in raw_value:
                raw_value = raw_value.split('#')[0].strip()
            current = raw_value.lower() in ('true', 'yes', '1', 'on')
        elif value_type == int:
            try:
                current = int(current.split('#')[0].strip())
            except:
                current = default
        
        print(f"\n{WizardColors.BOLD}{setting.replace('_', ' ').title()}:{WizardColors.END}")
        new_value = get_user_input(
            f"Value for {setting}",
            current,
            options,
            value_type,
            description
        )
        search_section[setting] = str(new_value)

def save_config(config):
    """Save the configuration to .config-bm file."""
    config_path = Path('.config-bm')
    
    # Create a nicely formatted config file
    content_lines = [
        "# Configuration file for Norwegian dictionary search (ordb)",
        "# Color customization settings",
        "",
        "[colors]",
        "# Main header colors",
        f"header = {config['colors']['header']}           # Search type headers (e.g., \"🔍 Exact search for...\")",
        f"lemma = {config['colors']['lemma']}             # Dictionary entry main word",
        f"bold = {config['colors'].get('bold', 'BOLD')}              # Bold text emphasis",
        "",
        "# Word class and grammatical info",
        f"word_class = {config['colors']['word_class']}      # [noun], [verb], [adj], etc.",
        f"masculine = {config['colors']['masculine']}         # masculine gender",
        f"feminine = {config['colors']['feminine']}           # feminine gender",
        f"neuter = {config['colors']['neuter']}           # neuter gender",
        "",
        "# Content colors",
        f"definition = {config['colors']['definition']}     # Definition text (no special color)",
        f"example = {config['colors']['example']}           # Example sentences",
        f"highlight = {config['colors']['highlight']}        # Search term highlighting",
        f"etymology = {config['colors']['etymology']}         # Etymology information",
        f"inflection_label = {config['colors']['inflection_label']}  # Inflection category labels",
        "",
        "# UI elements",
        f"error = {config['colors']['error']}              # Error messages",
        f"warning = {config['colors']['warning']}         # Warning messages",
        f"info = {config['colors']['info']}              # Informational text (separators, counts, etc.)",
        f"success = {config['colors']['success']}          # Success messages",
        "",
        "# Available color values:",
        "# DEFAULT (no color), BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, WHITE, GRAY",
        "# Style modifiers: BOLD, UNDERLINE",
        "# You can combine them like: BOLD_RED, UNDERLINE_BLUE, etc.",
        "",
        "[search]",
        "# Character replacement for easier keyboard input",
        "# When enabled, automatically tries alternative spellings when searching",
        f"character_replacement = {config['search']['character_replacement']}  # Replace aa→å, oe→ø, ae→æ in searches",
        "",
        "# Default limit for search results (can be overridden with --limit)",
        f"default_limit = {config['search']['default_limit']}  # Maximum number of results to show by default",
        "",
        "# Display options - control what information is shown by default",
        f"show_inflections = {config['search']['show_inflections']}   # Show inflection tables in output",
        f"show_etymology = {config['search']['show_etymology']}     # Show etymology information in output",
        "",
        "# Pagination settings for search results",
        f"pagination = {config['search']['pagination']}         # Enable pagination like 'more' command",
        f"page_size = {config['search']['page_size']}            # Number of lines per page (0 = auto-detect from terminal size)",
        f"limit_with_pagination = {config['search']['limit_with_pagination']}  # Max results when pagination is enabled",
        f"clear_screen = {config['search']['clear_screen']}      # Clear screen between pages (set to False if your terminal has issues)",
    ]
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))

def main():
    """Main configuration wizard."""
    print(f"{WizardColors.HEADER}{WizardColors.BOLD}")
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                Configuration Wizard                         │")
    print("│            Norwegian Dictionary Search (ordb)              │")
    print("└─────────────────────────────────────────────────────────────┘")
    print(f"{WizardColors.END}")
    
    print("This wizard will help you configure your .config-bm file.")
    print("Press Enter to keep current values, or type new values to change them.")
    print(f"{WizardColors.GRAY}Tip: You can always edit .config-bm manually later.{WizardColors.END}")
    
    # Load current configuration
    config = load_current_config()
    
    # Configure each section
    try:
        configure_colors(config)
        configure_search(config)
        
        # Confirm and save
        print(f"\n{WizardColors.BOLD}Configuration Summary:{WizardColors.END}")
        print("Your configuration is ready to be saved.")
        
        save_choice = input(f"\nSave configuration to .config-bm? [Y/n]: ").strip().lower()
        if save_choice in ('', 'y', 'yes'):
            save_config(config)
            print(f"{WizardColors.GREEN}✓ Configuration saved to .config-bm{WizardColors.END}")
            print("You can now use ordb with your new settings!")
        else:
            print(f"{WizardColors.YELLOW}Configuration not saved.{WizardColors.END}")
    
    except KeyboardInterrupt:
        print(f"\n{WizardColors.YELLOW}Configuration wizard cancelled.{WizardColors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{WizardColors.RED}Error: {e}{WizardColors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()