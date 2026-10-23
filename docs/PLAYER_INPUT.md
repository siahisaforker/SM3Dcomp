# PlayerInput: initial Wii U reconstruction

Source binary: US `RedCarpet.rpx`, SHA-256 `813d906365860eb6ef4644e8380983db382cbaefd951f9a89bd3d2c84eb4aaad`.

## Verified ranges

| Wii U `.text` range | Functions | Bytes | Source |
| --- | ---: | ---: | --- |
| `0x022B1A4C–0x022B1A64` | 1 | 24 | `PlayerInputReset.cpp` |
| `0x022B1A6C–0x022B1A74` | 1 | 8 | `PlayerInputFrame.cpp` |
| `0x022B2F28–0x022B2F64` | 3 | 60 | `PlayerInput.cpp` |
| `0x022B2F64–0x022B3024` | 23 | 192 | `PlayerInputAccessors.cpp` |

**Total: 28 matched functions / 284 matched bytes.** These are **matching-code ranges**, not claims of original Nintendo object-file boundaries. Every byte in each range matches the original PPC executable with GHS 5.3.22 `-Ospeed`.

## Reconstructed fields

| Wii U offset | Field | Supporting instruction |
| --- | --- | --- |
| `+0x0C` | stick-on flag | `lbz r3,0x0C(r3)` |
| `+0x10` | move vector | `addi r3,r3,0x10` |
| `+0x1C` | unarranged move vector | `addi r3,r3,0x1C` |
| `+0x28 / +0x2C` | stick X / Y | `lfs f1,...` |
| `+0x30` | jump button held | `lbz r3,0x30(r3)` |
| `+0x34` | frames since jump trigger | `lwz r3,0x34(r3)` and `isJumpTrigOn()` comparison with 10 |
| `+0x38` | jump button enabled | 0/1 stored by enable/disable |
| `+0x39 / +0x3A / +0x3B` | dash trigger / on / released | raw byte getters |
| `+0x3D / +0x3E` | squat trigger / button on | raw byte getters |
| `+0x3F / +0x40` | hip drop trigger / button on | raw byte getters |
| `+0x41` | fireball trigger | raw byte getter |
| `+0x44` | frames since swim paddle trigger | `isPrecedingSwimPaddleTrigOn()` comparison with 5 |
| `+0x48` | swim paddle trigger | raw byte getter |
| `+0x50` | frames since rolling trigger | `isRollingTrigOn()` comparison with 5 |
| `+0x54–+0x57` | bubble / climb trigger / climb on / hold on | raw byte getters |
| `+0x5A` | release trigger | raw byte getter |
| `+0x64` | invalidation-frame count | `stw r4,0x64(r3)` |

The Switch 3DWDecomp `PlayerInput` header corroborates the names and field order, but its structure places many corresponding fields **12 bytes later** and includes additional members. The Wii U offsets above are based on direct Wii U PPC disassembly and matching output; no Switch addresses were transplanted.

`is*()` flag accessors deliberately return `u8` rather than C++ `bool`: this GHS compiler emits an extra normalization sequence for `bool`, while the original Wii U instructions use direct `lbz` and `blr`. The raw bytes still represent boolean input flags. The accessor names correspond to the Switch interface and observed order; full virtual-table and caller verification is still needed for absolute naming confidence.

## Additional findings

`0x022B1A64–0x022B1A6C` is an 8-byte *this-adjustment thunk*: it subtracts 4 from `r3` and branches directly to `resetPrecedingJump()` at `0x022B1A4C`. It is not yet included as a source match. This is evidence of an interface subobject and a possible secondary base-class offset; the complete class inheritance layout is not established.

`0x022B3024` is a 92-byte, separate allocator/constructor-like function for a 0x1C-byte object, reached from `0x0224C644`. `0x022B3080` stores five incoming pointers/words into that object's offsets `+0x08` through `+0x18`; it is called from `0x0224C9F0`. **These are not PlayerInput instance accessors** simply because they are adjacent in executable code. `0x022B3098` is a 432-byte controller/collision-related routine reached from `0x0224D630`; exact class/function identity needs more analysis.

Next: identify the actual object constructor at `0x022B3024`, recover its vtable at `0x10320308`, and trace `0x0224C3C4` and `0x0224D454` through their interface use sites. In parallel, resolve `PlayerActionAirMove` virtual-method calls, including its confirmed `checkEndTurn` at `0x0224DE3C`.
