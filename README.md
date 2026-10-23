# SM3Dcomp

[![Code](https://bytematch.dev/siahisaforker/SM3Dcomp.svg?version=US&style=flat-square&label=Code&measure=matched_code_percent)](https://bytematch.dev/siahisaforker/SM3Dcomp) [![Data](https://bytematch.dev/siahisaforker/SM3Dcomp.svg?version=US&style=flat-square&label=Data&measure=matched_data_percent)](https://bytematch.dev/siahisaforker/SM3Dcomp) [![Functions](https://bytematch.dev/siahisaforker/SM3Dcomp.svg?version=US&style=flat-square&label=Functions&measure=matched_functions)](https://bytematch.dev/siahisaforker/SM3Dcomp) [![Units](https://bytematch.dev/siahisaforker/SM3Dcomp.svg?version=US&style=flat-square&label=Units&measure=complete_units)](https://bytematch.dev/siahisaforker/SM3Dcomp)

[![ByteMatch CI](https://github.com/siahisaforker/SM3Dcomp/actions/workflows/bytematch.yml/badge.svg)](https://github.com/siahisaforker/SM3Dcomp/actions/workflows/bytematch.yml)

A matching decompilation of **Super Mario 3D World (Wii U)**

## Status
| Metric | Matched |
| --- | --- |
| Code | 308 / 7,335,668 bytes (0.0042%) |
| Data | 0 / 4,036,468 initialized bytes (0%; not started) |

Progress reports are published via [ByteMatch](https://bytematch.dev/siahisaforker/SM3Dcomp).

## Quick start

```sh
git submodule update --init
python3 -m pip install -r requirements.txt
python3 configure.py compiler
python3 configure.py --rpx /path/to/your/RedCarpet.rpx --non-matching
python3 configure.py validate
ninja -j2 all_source
ninja -j2 verify
python3 configure.py
ninja -j2 progress
```

## Matching guidelines

see AGENTS.md (even if you aren't AI)

## AI use

most of this is AI with manual human intervention every time it cooks up some bullshit, I'm mainly doing this for SM3DW-modding, which will likely be mostly human. All of the tooling and stuff is written by AI, I plan on manually cleaning up later tho

update: i have to hold it's hand through the entire thing, so maybe the cleanup starts now lol
