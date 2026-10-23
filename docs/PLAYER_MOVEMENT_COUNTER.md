# Player movement-counter helper (US)

The US Wii U RPX stores a 28-byte polymorphic helper in the player-controller structure. The descriptive name `PlayerMovementCounter` is **provisional**: the vtable and behavior establish the object, but no Nintendo source symbol for the original class has been recovered.

## Data and creation

- The containing player-controller constructor at `0x0224C3C4` calls `0x022B3024` at `0x0224C644` with `r3 = 0`. The returned pointer is stored at parent offset `+0x8C`.
- `0x022B3024` accepts an optional existing object pointer, allocates `0x1C` bytes through `0x02369190` if null, assigns vtable `0x10320308`, and zeroes all remaining six 32-bit slots. Its code is 92 bytes and is **analyzed, not matched**.
- `0x0224C9F0` calls `0x022B3080` with the stored helper at `+0x8C` and five dependency pointers. This 24-byte function is **byte-for-byte matched** by `PlayerMovementCounter::bindDependencies`.
- `0x0224D630` calls `0x022B3098` with the same `+0x8C` object during the parent update. The 432-byte update is **analyzed, not matched**.

The object has this evidenced 32-bit memory layout:

| Offset | Description |
| --- | --- |
| `+0x00` | vtable, `0x10320308` |
| `+0x04` | frame counter, initially 0 |
| `+0x08` | dependency from outer controller `+0x50` |
| `+0x0C` | dependency from outer controller `+0x5C` |
| `+0x10` | dependency from outer controller `+0x0C` |
| `+0x14` | dependency from outer controller `+0x00` |
| `+0x18` | dependency supplied by outer constructor register `r29` |

The member field names are working descriptions. The exact game types of these pointers have not been independently identified.

## Original PPC for the matched binder

```asm
022B3080  stw r8,0x18(r3)
022B3084  stw r6,0x10(r3)
022B3088  stw r4,0x08(r3)
022B308C  stw r5,0x0C(r3)
022B3090  stw r7,0x14(r3)
022B3094  blr
```

The matching C++ source preserves the original store order with volatile pointer slots. GHS 5.3.22 otherwise reschedules these independent stores, producing semantically equivalent but nonmatching code.

## Virtual behavior

Four nonzero callback pointers were recovered from the original table at `0x10320308`:

| Table offset | Function | Evidence |
| --- | --- | --- |
| `+0x0C` | `0x022B3248` (192 bytes) | Converts counter and limit to floats, divides, clamps to `[0, 1]` |
| `+0x14` | `0x022B3308` (76 bytes) | Compares counter to an indirect limit; returns whether counter is at least the limit |
| `+0x24` | `0x022B3934` | Conditional deletion thunk |
| `+0x2C` | `0x022B3948` | Empty return thunk |

The limit is read through the pointer at helper offset `+0x18`, then `+0x6F4`, with the callback at that table's `+0x88C`. The normalized output uses constant `0.0f` from `0x10320300` and `1.0f` from `0x10320304`.

## Per-frame behavior under investigation

`0x022B3098` calls a virtual check on dependency `+0x0C` (vtable offset `+0x0C`), examines a result derived from dependency `+0x08`, and branches on movement/collision checks. In the true branch, it constructs an intermediate vector from dependency `+0x14`, conditionally compares its length against a player-supplied value, and increments the counter only while it is below the indirect maximum. In another branch it decrements a positive counter; otherwise it clears the counter to zero.

This is evidence of a *movement-dependent frame accumulator*, but it does **not** prove that the counter represents an exact mechanic such as wall running, slope contact, or dash charge. The dependency virtual functions at `0x02259B48`, `0x0227FCA0`, `0x0227EC60`, and `0x02280240` still require identification.

## Next matching targets

- `0x022B3024` (92 bytes): recover the original allocation-aware constructor and vtable setup without hard-coding a false type identity.
- `0x022B3248` (192 bytes): match the normalized counter-ratio callback after recovering the exact float-conversion sequence.
- `0x022B3308` (76 bytes): match the maximum-counter predicate.
- `0x022B3098` (432 bytes): map and type all indirect dependencies before reconstructing the update logic.

These are investigation targets, **not** verified byte matches. This note keeps their Ghidra labels suffixed `Candidate`. The small `PlayerMovementCounter.cpp` source is an isolated matching split; there is no claim it reflects the original game's object-file boundaries.
