# SM3Dcomp

[![Code progress](https://bytematch.dev/siahisaforker/SM3Dcomp.svg?label=Code&measure=matched_code_percent&version=US)](https://bytematch.dev/siahisaforker/SM3Dcomp)

A matching decompilation of **Super Mario 3D World (Wii U)**

## Status
308 / 7,335,668 bytes matched (0.0042%)


Progress reports are published via [ByteMatch](https://bytematch.dev/siahisaforker/SM3Dcomp) after project registration. See [ByteMatch integration](docs/BYTEMATCH.md).

## Quick start

```sh
git submodule update --init
python3 -m pip install -r requirements.txt
tools/setup_compiler.sh
python3 configure.py --rpx /path/to/your/RedCarpet.rpx --non-matching
python3 tools/validate_splits.py
ninja -j2 all_source
ninja -j2 verify
python3 configure.py
ninja -j2 progress
```
## AI use

most of this is AI with manual human intervention every time it cooks up some bullshit, I'm mainly doing this for SM3DW-modding, which will likely be mostly human. All of the tooling and stuff is written by AI, I plan on manually cleaning up later tho