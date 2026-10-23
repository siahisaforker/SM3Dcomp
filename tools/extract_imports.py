#!/usr/bin/env python3

"""Extract dynamic function/data imports from a decompressed Wii U RPX ELF."""

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ELF = ROOT / "build" / "US" / "orig" / "RedCarpet.elf"
DEFAULT_OUTPUT = ROOT / "config" / "US" / "imports"


@dataclass(frozen=True)
class Section:
    name: str
    kind: int
    offset: int
    size: int
    link: int
    entsize: int


@dataclass(frozen=True)
class Import:
    section: str
    name: str
    address: int
    kind: str


def fail(message):
    raise ValueError(message)


def get_string(data, offset):
    if offset < 0 or offset >= len(data):
        fail("invalid string table offset")
    end = data.find(b"\0", offset)
    if end < 0:
        fail("unterminated ELF string")
    return data[offset:end].decode("utf-8")


def read_imports(data):
    if len(data) < 52 or data[:7] != b"\x7fELF\x01\x02\x01":
        fail("expected a big-endian ELF32 file")
    elf_type, machine = struct.unpack_from(">HH", data, 16)
    if elf_type != 0xFE01 or machine != 20:
        fail("expected a Wii U PowerPC RPX ELF")
    shoff = struct.unpack_from(">I", data, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from(">HHH", data, 46)
    if shentsize != 40 or shnum == 0 or shstrndx >= shnum:
        fail("invalid ELF section headers")
    if shoff + shnum * shentsize > len(data):
        fail("ELF section headers outside file")
    raw = [struct.unpack_from(">IIIIIIIIII", data, shoff + index * shentsize)
           for index in range(shnum)]

    def section_data(header):
        _, kind, _, _, offset, size, _, _, _, _ = header
        if kind == 8 or offset + size > len(data):
            fail("ELF section data outside file")
        return data[offset:offset + size]

    section_names = section_data(raw[shstrndx])
    sections = [Section(get_string(section_names, header[0]), header[1], header[4],
                        header[5], header[6], header[9]) for header in raw]
    imports = []
    seen = {}
    for section_index, section in enumerate(sections):
        if section.kind != 2:  # SHT_SYMTAB
            continue
        if section.entsize != 16 or section.size % section.entsize or section.link >= shnum:
            fail("invalid ELF symbol table")
        strings = section_data(raw[section.link])
        symbols = section_data(raw[section_index])
        for offset in range(0, len(symbols), 16):
            name_offset, address, size, info, other, index = struct.unpack_from(">IIIBBH", symbols, offset)
            if index >= shnum:
                continue
            section_name = sections[index].name
            if not section_name.startswith((".fimport_", ".dimport_")):
                continue
            kind = info & 15
            binding = info >> 4
            expected = 2 if section_name.startswith(".fimport_") else 1
            if kind != expected or binding not in (1, 2):
                continue
            name = get_string(strings, name_offset)
            if not name or any(char.isspace() or char in ";=#" for char in name):
                fail("invalid imported symbol name")
            if name in seen and seen[name] != (address, section_name):
                fail(f"conflicting imported symbol {name}")
            seen[name] = (address, section_name)
            imports.append(Import(section_name, name, address, "function" if kind == 2 else "data"))
    if not imports:
        fail("no imported symbols found")
    return sorted(set(imports), key=lambda item: (item.section, item.address, item.name))


def import_files(imports):
    groups = {}
    for item in imports:
        suffix = item.section.split("import_", 1)[1].removesuffix(".rpl")
        name = suffix + ("_data" if item.kind == "data" else "") + ".txt"
        groups.setdefault(name, []).append(item)
    rendered = {}
    for name, entries in sorted(groups.items()):
        section_name = entries[0].section
        lines = [f"// RedCarpet.rpx {section_name} symbols.",
                 "// Generated from the original RPX symbol table. Do not edit manually.", ""]
        lines += [f"{item.name} = 0x{item.address:08x};" for item in entries]
        rendered[name] = "\n".join(lines) + "\n"
    return rendered


def run(elf, output, check):
    expected = import_files(read_imports(elf.read_bytes()))
    existing = {path.name for path in output.glob("*.txt")}
    if check:
        problems = [name for name, text in expected.items()
                    if not (output / name).is_file() or (output / name).read_text() != text]
        problems += sorted(existing - expected.keys())
        if problems:
            fail("stale import maps: " + ", ".join(sorted(problems)))
    else:
        output.mkdir(parents=True, exist_ok=True)
        for name, text in expected.items():
            path = output / name
            if not path.is_file() or path.read_text() != text:
                path.write_text(text)
    print(f"{sum(len(text.splitlines()) - 3 for text in expected.values())} imported symbols "
          f"in {len(expected)} maps ({'verified' if check else 'generated'})")
    return sorted(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, default=DEFAULT_ELF)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        run(args.elf, args.output, args.check)
    except (ValueError, OSError) as error:
        parser.exit(1, f"import extraction: {error}\n")


if __name__ == "__main__":
    main()
