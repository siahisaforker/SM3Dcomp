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

GHS 5.3.22 predates modern C++ features. Prefer `typedef` over `using`, and avoid lambdas or STL-heavy implementations. Do not add modern features until verified with the exact compiler.

Place source code in `src/Game/<Subsystem>/<Class>.cpp` and declarations in `include/Game/<Subsystem>/<Class>.h`. Use a single conceptual translation unit per original object if its boundary is known. Keep symbols and offsets in the manifest rather than scattering addresses through gameplay code.

Comments should communicate necessary ABI restrictions or reverse-engineering uncertainty only. Do not leave explanatory filler, tool transcripts, or AI attribution comments in code.

## Headers, translation units, and formatting

Keep types, external function declarations, and shared interfaces in headers. Keep game function
implementations out-of-line in `.cpp` files: for a matching decompilation, the compiler must emit
a specific standalone symbol, and grouping functions or defining them inline in headers can change
code generation and matching boundaries. Combine adjacent functions in one source file only after
verifying that their original ranges and the compiled output permit it.

Use the repository's `.clang-format` for C++ and close each namespace with a comment such as
`} // namespace sm3d`. Keep version-specific PowerPC overrides
separate from the readable C++ body and gated behind `INLINE_HACKS`.

## Partial layouts

Expose normal class interfaces in public headers. Do not implement guessed methods with raw
pointer-offset wrappers or manufactured vtables: keep unresolved declarations until their actual
class layout and implementations are recovered. Do not fabricate large padding arrays to access a
single member or put compiler-specific size assertions in gameplay headers. Check observed offsets
in independent tests instead.

`PlayerInput`'s Wii U constructor at `0x022B1A74` initializes three vtable pointers at offsets
`0`, `4`, and `8`. The corresponding input-related interface names are corroborated by the Switch
reference but are not yet verified Wii U base classes. Its remaining identified field offsets and
`0x80`-byte size were checked with the original Nintendo GHS compiler. Keep any truly unidentified
field unnamed rather than inventing a gameplay purpose. Reconstruct inheritance before replacing
these transitional vtable members with base-class declarations.

`INLINE_HACKS` provides the optional US executable assembly-exact version of the movement update.
This is separate from source-to-compiler matching and must not inflate the normal match count.

Matching and source organization are distinct: a function-level matching split is not proof of
an original object-file boundary. `PlayerMovementCounter::update()` is still a non-matching C++
reconstruction because dependency method implementations are unresolved. The optional assembly
version can reproduce the original US bytes, but is not a source-level compiler match.
