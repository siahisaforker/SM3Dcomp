#!/usr/bin/env python3

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "US"
SYMBOL_RE = re.compile(
    r"^([^=\s]+)\s*=\s*(\.[\w.$]+):(0x[0-9a-fA-F]+|\d+)\s*;\s*(?://\s*size:\s*(0x[0-9a-fA-F]+|\d+))?\s*$"
)
SPLIT_RE = re.compile(
    r"^\s+(\.[\w.$]+)\s+start:(0x[0-9a-fA-F]+|\d+)\s+end:(0x[0-9a-fA-F]+|\d+)\s*$"
)
EXPECTED_RPX_SHA256 = "813d906365860eb6ef4644e8380983db382cbaefd951f9a89bd3d2c84eb4aaad"
TEXT_START = 0x02000020
TEXT_END = 0x026FEF14


def fail(message):
    raise ValueError(message)


def read_symbols(path):
    result = []
    seen_names = set()
    seen_addresses = set()
    for line_number, original in enumerate(path.read_text().splitlines(), 1):
        line = original.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        match = SYMBOL_RE.fullmatch(line)
        if not match:
            fail(f"{path}:{line_number}: malformed symbol")
        name, section, raw_address, raw_size = match.groups()
        if not raw_size:
            fail(f"{path}:{line_number}: function size is required")
        address, size = int(raw_address, 0), int(raw_size, 0)
        if name in seen_names or (section, address) in seen_addresses:
            fail(f"{path}:{line_number}: duplicate name or address")
        if section == ".text" and (address % 4 or size % 4):
            fail(f"{path}:{line_number}: PowerPC instructions must be 4-byte aligned")
        if size <= 0:
            fail(f"{path}:{line_number}: non-positive function size")
        seen_names.add(name)
        seen_addresses.add((section, address))
        result.append((name, section, address, address + size))
    return result


def read_splits(path):
    result = []
    current_source = None
    seen_sources = set()
    for line_number, original in enumerate(path.read_text().splitlines(), 1):
        line = original.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if not original[:1].isspace() and line.endswith(":"):
            current_source = line[:-1]
            if current_source in seen_sources or ".." in Path(current_source).parts:
                fail(f"{path}:{line_number}: duplicate or unsafe source path")
            seen_sources.add(current_source)
            if not (ROOT / "src" / current_source).is_file():
                fail(f"{path}:{line_number}: missing source: {current_source}")
            continue
        match = SPLIT_RE.fullmatch(original)
        if current_source is None or not match:
            fail(f"{path}:{line_number}: malformed split")
        section, raw_start, raw_end = match.groups()
        start, end = int(raw_start, 0), int(raw_end, 0)
        if start >= end:
            fail(f"{path}:{line_number}: empty or reversed range")
        if section == ".text":
            if start < TEXT_START or end > TEXT_END or start % 4 or end % 4:
                fail(f"{path}:{line_number}: out-of-bounds or unaligned .text")
        result.append((current_source, section, start, end))
    if not result:
        fail(f"{path}: no source units")
    for section in {item[1] for item in result}:
        ranges = sorted((start, end, source) for source, sec, start, end in result if sec == section)
        for (_, earlier_end, earlier_source), (start, _, source) in zip(ranges, ranges[1:]):
            if start < earlier_end:
                fail(f"overlap in {section}: {earlier_source} / {source} at 0x{start:08x}")
    return result


def validate():
    active = read_symbols(CONFIG / "symbols.txt")
    verified = read_symbols(CONFIG / "verified_symbols.txt")
    splits = read_splits(CONFIG / "splits.txt")
    verification = {(section, start, end) for _, section, start, end in verified}
    active_ranges = sorted((start, end) for _, section, start, end in active if section == ".text")
    for (_, prev_end), (start, _) in zip(active_ranges, active_ranges[1:]):
        if start < prev_end:
            fail(f"active symbol overlap at 0x{start:08x}")
    for name, section, start, end in active:
        covering = [s for s in splits if s[1] == section and s[2] <= start and end <= s[3]]
        if len(covering) != 1:
            fail(f"{name}: must be contained in exactly one matching split")
        if (section, start, end) not in verification:
            fail(f"{name}: no identically bounded verified PowerPC function")
    for source, section, start, end in splits:
        if not any(sym_section == section and sym_start >= start and sym_end <= end
                   for _, sym_section, sym_start, sym_end in active):
            fail(f"{source}: no named function in split 0x{start:08x}-0x{end:08x}")
    rp = ROOT / "orig" / "US" / "RedCarpet.rpx"
    if rp.is_file():
        actual = hashlib.sha256(rp.read_bytes()).hexdigest()
        if actual != EXPECTED_RPX_SHA256:
            fail(f"original executable SHA-256 differs: {actual}")
    covered = sum(end - start for _, section, start, end in splits if section == ".text")
    rp_status = "RPX fingerprint verified" if rp.is_file() else "RPX not present"
    print(f"valid: {len(splits)} split ranges, {len(active)} matching targets, "
          f"{len(verified)} verified research symbols, {covered} bytes of active text; "
          f"{rp_status}")


if __name__ == "__main__":
    try:
        validate()
    except ValueError as exc:
        print(f"invalid splits: {exc}", file=sys.stderr)
        sys.exit(1)
