# C++ style and names

Decompiled source should resemble maintainable game code while staying faithful to the PowerPC compiler and original binary.

| Kind | Convention | Example |
| --- | --- | --- |
| Class, struct, enum, type | PascalCase | `PlayerInput`, `ActionState` |
| Class translation unit/header | PascalCase | `Game/Player/PlayerInput.cpp` |
| Method, free function, local, parameter | camelCase | `isRollingTrigOn`, `frameCount` |
| Known member field | camelCase | `rollingTriggerFrames` |
| Unknown raw layout span | `unknownXX` until identified | `unknown54` |
| Python tools, research filenames | snake_case | `validate_splits.py` |
| Compile-time constant | `kPascalCase` | `kRollingBufferFrames` |
| Namespaces | lowercase | `sm3d` |

Keep original game naming when strong source evidence shows it; do not rename functions solely to satisfy style. Use braces on a new line for definitions and control blocks. Use four-space indentation, explicit fixed-size integer aliases from `types.h`, and no exceptions or RTTI.

GHS 5.3.22 predates modern C++ features. Prefer `typedef` and typedef-char size checks over `using`, `static_assert`, lambda expressions, or STL-heavy implementations. Do not add modern features until verified with the exact compiler.

Place source code in `src/Game/<Subsystem>/<Class>.cpp` and declarations in `include/Game/<Subsystem>/<Class>.h`. Use a single conceptual translation unit per original object if its boundary is known. Keep symbols and offsets in the manifest rather than scattering addresses through gameplay code.

Comments should communicate necessary ABI restrictions or reverse-engineering uncertainty only. Do not leave explanatory filler, tool transcripts, or AI attribution comments in code.
