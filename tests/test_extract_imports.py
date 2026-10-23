import struct
import tempfile
import unittest
from pathlib import Path

from tools.extract_imports import import_files, read_imports, run


def sample_elf():
    names = ["", ".shstrtab", ".strtab", ".symtab", ".fimport_coreinit", ".dimport_coreinit"]
    section_strings = bytearray(b"\0")
    offsets = {"": 0}
    for name in names[1:]:
        offsets[name] = len(section_strings)
        section_strings.extend(name.encode() + b"\0")
    symbols_strings = b"\0OSGetCoreId\0MEMAllocFromDefaultHeap\0"
    symbols = bytearray(16)
    symbols.extend(struct.pack(">IIIBBH", 1, 0xC0001008, 0, 0x12, 0, 4))
    symbols.extend(struct.pack(">IIIBBH", 13, 0xC0002008, 0, 0x11, 0, 5))
    contents = bytearray(52)
    def append(data):
        while len(contents) % 4:
            contents.append(0)
        start = len(contents)
        contents.extend(data)
        return start
    name_offset = append(section_strings)
    symbol_name_offset = append(symbols_strings)
    symbol_offset = append(symbols)
    header_offset = append(b"\0" * (6 * 40))
    for index, name in enumerate(names):
        kind = 3 if index in (1, 2) else (2 if index == 3 else 0)
        offset = {1: name_offset, 2: symbol_name_offset, 3: symbol_offset}.get(index, 0)
        size = {1: len(section_strings), 2: len(symbols_strings), 3: len(symbols)}.get(index, 0)
        link = 2 if index == 3 else 0
        entsize = 16 if index == 3 else 0
        struct.pack_into(">IIIIIIIIII", contents, header_offset + 40 * index,
                         offsets[name], kind, 0, 0, offset, size, link, 0, 4, entsize)
    contents[0:7] = b"\x7fELF\x01\x02\x01"
    struct.pack_into(">HH", contents, 16, 0xFE01, 20)
    struct.pack_into(">I", contents, 32, header_offset)
    struct.pack_into(">HHH", contents, 46, 40, 6, 1)
    return bytes(contents)


class ImportExtractorTests(unittest.TestCase):
    def test_function_and_data_imports(self):
        imports = read_imports(sample_elf())
        self.assertEqual(len(imports), 2)
        rendered = import_files(imports)
        self.assertEqual(set(rendered), {"coreinit.txt", "coreinit_data.txt"})
        self.assertIn("OSGetCoreId = 0xc0001008;", rendered["coreinit.txt"])
        self.assertIn("MEMAllocFromDefaultHeap = 0xc0002008;", rendered["coreinit_data.txt"])

    def test_regeneration_and_drift_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            elf = Path(directory) / "game.elf"
            output = Path(directory) / "imports"
            elf.write_bytes(sample_elf())
            self.assertEqual(len(run(elf, output, False)), 2)
            self.assertEqual(len(run(elf, output, True)), 2)
            (output / "coreinit.txt").write_text("changed\n")
            with self.assertRaisesRegex(ValueError, "stale import maps"):
                run(elf, output, True)

    def test_rejects_wrong_elf(self):
        with self.assertRaisesRegex(ValueError, "big-endian ELF32"):
            read_imports(b"not an ELF")
        damaged = bytearray(sample_elf())
        damaged[18] = 0
        damaged[19] = 3
        with self.assertRaisesRegex(ValueError, "Wii U PowerPC"):
            read_imports(bytes(damaged))


if __name__ == "__main__":
    unittest.main()
