also written by codex, maybe it's a bit easier to digest by llms? might replace later

# Matching workflow

## What the manifests mean

- `config/US/config.yml`: supported RPX, text address, compiler, and toolchain.
- `config/US/verified_symbols.txt`: independently supported Wii U names and exact known code bounds. **Not** automatically compiled.
- `config/US/symbols.txt`: named functions that currently have source participating in matching.
- `config/US/splits.txt`: per-source *half-open* `[start, end)` linker ranges for units currently being matched.
- `.local/function_inventory.txt`: Ghidra-derived addresses and provisional function boundaries, when generated. Research material, **not** a linkable split manifest.
- `.local/restart-20261022/`: archived previous tracked tree, old manifests, and baseline report.

The active split file deliberately does **not** pretend that all ~7 MB has been recovered. A function address is not proof of an object-file boundary. Unassigned text remains unmatched/unclaimed.

## Adding a unit

1. Locate the function in the Wii U Ghidra project and inspect its PowerPC disassembly, references, and any jump tables or merged thunks. Validate the executable fingerprint.
2. Record its entry, size, end-exclusive boundary, original behavior and confidence. Source names must be defensible, not guessed from Switch addresses.
3. Determine the probable original object grouping. Adjacent small functions from the same object can share a split, but never overlap another unit.
4. Create the minimal class declaration/implementation. Keep pointer widths and layout explicit, and beware GHS 5.3.22 language support and optimization behavior.
5. Append matching-source symbols to `symbols.txt` and the corresponding source range to `splits.txt`. Include every active symbol within exactly one split. Rerun the validator before configuring.
6. Configure in non-matching mode, compile with `-j2`, compare disassembly/objdiff, and iterate locally.
7. Run the strict match. Update progress only after byte verification. Do not label a compile-only unit as matched.

## Evidence levels

- **Candidate**: string reference, nearby function, similar constant, or Switch call graph only.
- **Verified identity**: Wii U PPC control flow, callers, data layout and semantics establish a name, but source may not yet match.
- **Matching**: compiled GHS source and original RPX bytes are identical for the declared sections.

The original `RedCarpet.rpx` SHA-256 is:
`813d906365860eb6ef4644e8380983db382cbaefd951f9a89bd3d2c84eb4aaad`.

Do not assume Wii U functions exist simply because Bowser's Fury/Switch has one. In particular, Fury's aerial dive may need new game logic rather than mapping an existing Wii U action. Keep `SM3DW-modding` and the installed Fury physics plugin independent of this decomp.

## Fuzzy candidates

A fuzzy candidate is normal C++ source whose GHS output is not byte-exact. Declare it in
`config/US/fuzzy_functions.json`, **not** in the strict `splits.txt` or `symbols.txt`.
Running `python3 tools/bytematch_report.py update` locally compiles the ordinary C++ branch
(without `INLINE_HACKS`) and compares PowerPC opcode sequences to the original RPX using an
order-preserving sequence alignment that ignores register selection and operands. The
`ppc_opcode_sequence_v1` score is an approximation, not objdiff's instruction/operand-aware
similarity algorithm or evidence of functional correctness. The input hashes, measured score,
compiler-emitted size, and number of aligned opcode words are stored in the verified snapshot;
CI renders only this snapshot without requiring Nintendo's compiler or the RPX.

The report exposes fuzzy percentage separately at function, unit, and project levels.
Fuzzy units occupy their original text range but contribute **zero** exact-matched bytes,
functions, or completed units. Remove fuzzy entries when strict verification becomes possible.

## Reproducibility

```sh
python3 tools/validate_splits.py
python3 configure.py --non-matching
ninja -j2 all_source
ninja -j2 verify
python3 configure.py
ninja -j2 progress
```

`--non-matching` allows analysis of mismatches. The last configure removes that allowance. Generated build outputs, Ghidra projects and original executables are intentionally excluded from Git.

## Ghidra function inventory

To regenerate the separate research-only list after importing/analyzing the RPX:

```sh
tools/analyzeHeadless /path/to/ghidra-projects PROJECT_NAME \
  -process RedCarpet.rpx -noanalysis \
  -scriptPath tools/ghidra_scripts \
  -postScript ExportFunctionInventory.java .local/function_inventory.txt
```

The current local analysis identified 30,964 function entries, of which 86 have fragmented bodies. This count is not a measure of decompilation progress. The export is intentionally ignored, and includes tentative Ghidra function names; manually verify function extents and original object boundaries before editing `splits.txt`.
