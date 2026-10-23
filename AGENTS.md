# Guidelines

## Matching

- Match the US Wii U executable with GHS 5.3.22.
- Verify function boundaries, symbols, and layouts against the original PowerPC code.
- Keep splits accurate and don't guess missing code or structures.
- Only count byte-identical compiled code as matched. Keep fuzzy matches separate.
- Run `python3 configure.py validate`, `ninja -j2 progress`, and `python3 tools/bytematch_report.py check` before claiming a match.

## Code quality

- Write clean, readable C++ compatible with GHS. No assembly hacks.
- Follow `.clang-format`: four spaces, Allman braces, PascalCase types and camelCase members.
- Keep headers and source files organized by subsystem.
- Don't add filler comments, unnecessary wrappers, or dead code.
- Don't change unrelated files unless asked.


If you are not an AI, this might apply to you still! just don't count the last bullet point of the matching guidelines