well, if you're gonna use ai, might as well do it right!
instructions written by codex, change later when we actually have standards

# SM3Dcomp contributor instructions

This is a **matching PowerPC decompilation** of the US Wii U version of Super Mario 3D World. It is not a rewrite, a Switch port, a runtime mod, or a Ghidra pseudocode dump.

## Non-negotiable rules

- Preserve the original RPX and its SHA-256. Never commit executable or game assets.
- Inspect `git status --short` before editing. Do not overwrite unrelated work. Do not commit, push, or publish unless explicitly requested.
- Use the pinned GHS 5.3.22 compiler with the existing Ninja/objdiff toolchain; modern C++ syntax may not compile.
- Only call a function **matched** when its exact original bytes pass the matching verifier. Compilation, similarity, or Ghidra identification alone do not count.
- Keep provisional Ghidra names and inferred addresses separate from build-active symbols.
- Switch/3DWDecomp is a semantic reference only: Switch ARM64 addresses and object layouts are never transferable Wii U offsets.
- Do not fill unknown spans with guessed source, fake symbol names, padding, or guessed object boundaries to improve statistics.
- Do not alter optimization flags or source unrelated to the function being matched as a shortcut.
- Avoid boilerplate comments, speculation presented as fact, extra scripts, and unsolicited repository cleanup.

## Naming and style

Follow `docs/STYLE.md`: PascalCase for classes, structs, enums, class-derived source filenames; camelCase for methods, variables, fields; snake_case for tool scripts and temporary analysis artifacts. Name known functions semantically, and unknown ones `FUN_XXXXXXXX` only in the *research* inventory. Keep the original game symbol spelling when authoritative. Write declarations in `include/` and implementations in `src/` by subsystem.

## Before any function edit

1. Confirm the RPX fingerprint and the address against Ghidra PowerPC instructions.
2. Find the actual function entry, end-exclusive address, callers, and relevant relocation/string evidence. Record what is proved versus inferred.
3. Put a confirmed human-readable name in `config/US/verified_symbols.txt`. Only add it to the active `symbols.txt` once there is matching-target source.
4. Add the smallest defensible nonoverlapping range to `splits.txt`; split at *original object boundaries* when known. Do not assume source object boundaries from a Ghidra function boundary.
5. Implement equivalent logic with explicit 32-bit layout assumptions, avoiding UB and unjustified casts.

## Verification loop

```sh
python3 tools/validate_splits.py
python3 configure.py --non-matching
ninja -j2 all_source
ninja -j2 verify
python3 configure.py
ninja -j2 progress
```

Use `--non-matching` **only during iteration**. The strict verification is the acceptance criterion. If strict verification fails, state the function as non-matching, report concrete byte/size/instruction differences, and keep progress honest. Prefer objdiff or PowerPC objdump over changing source blindly.

Update research/provenance as you work, but do not inflate verified or matched counts. Preserve Ghidra projects, compiler binaries, original game data, and temporary builds under ignored `.local/` or `build/`. Check `docs/MATCHING.md` before changing split or linker logic.
