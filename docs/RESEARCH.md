# Current Wii U research status

The restart intentionally discarded the old *matching claim* while preserving its code and metadata in the ignored archive at `.local/restart-20261022/previous-tracked-tree.tar.gz`. Git history is unchanged. The original RPX, compiler toolchain, and Ghidra project remain available.

## Established

- Strict GHS 5.3.22 build: 3/3 `PlayerInput` trigger predicates match all 60 original instruction bytes, from `0x022B2F28` through `0x022B2F64` (exclusive).
- 24 identified Wii U functions are in the separate `config/US/verified_symbols.txt` and are **not** automatically counted as matched.
- Latest Ghidra project export: 30,941 function entries, including 86 noncontiguous bodies. The inventory resides in ignored `.local/function_inventory.txt`; do not treat these as original object boundaries.
- The original RPX SHA-256 remains `813d906365860eb6ef4644e8380983db382cbaefd951f9a89bd3d2c84eb4aaad`.

## Action-graph work still pending

- `PlayerActionGraph::checkShift`, `checkShiftCondition`, the ground-to-dash-roll predicate and air normal-speed getter have no sufficiently verified Wii U addresses yet.
- Wii U `0x022AD2D0` transitions *player forms*, not necessarily action-graph nodes. Do **not** label it `PlayerActionGraph::checkShift`.
- Wii U `0x0227A5CC` constructs a 0x2C-byte multi-vtable object used by the large builder at `0x02259C4C`; its exact action/condition identity is unproven.
- Wii U `0x0228DE90` calls the verified `PlayerInput::update` and other input helpers. Its player-update wrapper identity should be confirmed before naming.
- The Switch/Fury `PlayerActionDive` implementation is not proof of an equivalent Wii U action. A new dive may require mod/plugin logic rather than decompiling a nonexistent class.

The original Ghidra analysis logs remain under `.local/analysis-reports/`, and the new investigation logs are under `.local/restart-20261022/`. Avoid renaming, patching or exposing unverified action-graph targets until their PowerPC instruction and call-graph behavior is established.
