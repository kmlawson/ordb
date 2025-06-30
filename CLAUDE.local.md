# Claude Code Guidelines

- This tool ordb was created in June, 2025 by Claude Code with Konrad Lawson at the controls
- This file contains guidelines for Claude Code to keep in context as it works with the files:
- Always begin by reading README.md for overview of this software. 

## Structure

- Directory structure should adhere to requirements of PyPi
- Database related files and scripts in directory db/
- Documentation related files in directory docs/
- Tests available in directory tests/
- Main scripts in src/

## Testing Driven Development

- whenever you are going to create a new feature, create a test for it first in tests/ which fails and then implement the feature, and get the test passing. 

## General Guidelines

- Whenever you fix, add, or change things, be sure to update the CHANGELOG. 
- Only push origin to github when I give you the word, but you can commit when completing a fix. When commiting to git, only make version bumps (minor and match) with confirmation from the user, and then according to semantic versioning principals. Confirm with user when doing this. 
- We are never at 1.0 until the user explicitly says we are. 
- If you have to recreate the database using json-to-db.py (and please do not create more of these, just edit the one you have) then keep in mind that the database may have to be regenerated multiple times and it keeps the replacements of abbreviations etc. that were fixed in previous versions. 
- The ordb command should produce similarly comprehensive results as the web version of hte same. Any of those words can be found in its official online version with https://ordbokene.no/nno/bm/[search term] so, ordb hus should roughly produce similar content as https://ordbokene.no/nno/bm/hus and so on. I will often complain when data is present in the web version but not found in the output of the script. 
- problems and future features are listed in TODO.md - when you complete one of the items, put a green check mark at the beginning of the bullet point. 
- When you fix things or add features, don't delete existing functionality.
- Always fix things for general application, you MUST NOT hard code fixes for a specific word.
- when you fix something, make a test to check for it in future, and save all tests in the directory "tests"
- YOU MUST NOT forget to read files before you write to them.

