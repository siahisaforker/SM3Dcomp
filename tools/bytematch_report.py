#!/usr/bin/env python3

import argparse
from difflib import SequenceMatcher
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from configure import (
    extract_elf_range,
    file_sha256,
    is_verification_fresh,
    load_project,
    load_symbols,
    load_undefined_maps,
    load_units,
)

VERSION = "US"
SNAPSHOT = ROOT / "config" / VERSION / "bytematch_snapshot.json"
OUTPUT = ROOT / "build" / VERSION / "bytematch" / "report.json"
FUZZY_MANIFEST = ROOT / "config" / VERSION / "fuzzy_functions.json"
TEXT_BASE = 0x02000020
INVENTORY_FUNCTIONS = 30964


def fail(message):
    raise ValueError(message)


def input_hashes():
    files = [ROOT / "configure.py", ROOT / "CMakeLists.txt", ROOT / "tools" / "validate_splits.py"]
    for directory in (ROOT / "config" / VERSION, ROOT / "src", ROOT / "include"):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and path != SNAPSHOT and "__pycache__" not in path.parts)
    return {str(path.relative_to(ROOT)): file_sha256(path)
            for path in sorted(files)}


def original_data_sections(path):
    data = path.read_bytes()
    if data[:7] != b"\x7fELF\x01\x02\x01":
        fail("expected decompressed big-endian Wii U ELF")
    header = struct.unpack_from(">I", data, 32)[0]
    size, count, names_index = struct.unpack_from(">HHH", data, 46)
    if size != 40 or not 0 <= names_index < count or header + count * size > len(data):
        fail("invalid original ELF section headers")
    headers = [struct.unpack_from(">IIIIII", data, header + i * size)
               for i in range(count)]
    _, _, _, _, offset, length = headers[names_index]
    if offset + length > len(data):
        fail("invalid original section-name table")
    names = data[offset:offset + length]
    found = {}
    for name_offset, section_type, flags, address, offset, length in headers:
        if name_offset >= len(names):
            continue
        name = names[name_offset:].split(b"\0", 1)[0].decode("utf-8")
        if name not in (".rodata", ".data"):
            continue
        if name in found or section_type != 1 or flags & 0x08000000 or offset + length > len(data):
            fail("invalid or compressed initialized data section: " + name)
        found[name] = {"name": name, "address": address, "size": length}
    if set(found) != {".rodata", ".data"}:
        fail("missing original initialized data sections")
    return [found[".rodata"], found[".data"]]


def project_units():
    project = load_project(ROOT, VERSION)
    symbols = load_symbols(ROOT / project.symbols)
    units = load_units(ROOT, project, symbols)
    return project, units


def unit_match_records(project, units):
    undefined = load_undefined_maps(ROOT, project.undefined_maps + project.import_maps)
    build_root = ROOT / "build" / VERSION
    records = []
    for unit in units:
        fresh_sections = {section.name: section for section in unit.sections
                          if is_verification_fresh(ROOT, build_root, project, unit, section,
                                                   undefined)}
        for function in unit.functions:
            if ".text" in fresh_sections:
                records.append({"name": function.name, "address": function.address,
                                "size": function.size, "unit": unit.name})
    return sorted(records, key=lambda item: (item["address"], item["name"]))


def fuzzy_manifest():
    if not FUZZY_MANIFEST.is_file():
        return []
    candidates = json.loads(FUZZY_MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        fail("fuzzy manifest must be a list")
    seen = set()
    for item in candidates:
        if not isinstance(item, dict) or set(item) != {"name", "unit", "source_path", "address", "size"}:
            fail("invalid fuzzy function manifest entry")
        try:
            address = int(item["address"], 0)
        except (ValueError, TypeError):
            fail("invalid fuzzy function address")
        if (not item["name"] or not item["unit"] or
                type(item["size"]) is not int or item["size"] <= 0 or
                address % 4 or item["size"] % 4 or
                not item["source_path"].startswith("src/") or
                not (ROOT / item["source_path"]).is_file()):
            fail("invalid fuzzy function declaration")
        key = (item["unit"], item["name"], address)
        if key in seen:
            fail("duplicate fuzzy function")
        seen.add(key)
    return candidates


def opcode_tokens(code):
    if len(code) % 4:
        fail("PowerPC instruction sequence is not word aligned")
    for (word,) in struct.iter_unpack(">I", code):
        opcode = word >> 26
        # Extended-opcode instructions need the XO field to distinguish operations.
        yield (opcode, (word >> 1) & 1023) if opcode in (4, 19, 31, 59, 63) else (opcode,)


def measure_fuzzy(project):
    """Compare the ordinary GHS C++ object to original PPC, never INLINE_HACKS."""
    results = []
    output = ROOT / "build" / VERSION / "fuzzy"
    output.mkdir(parents=True, exist_ok=True)
    wibo = ROOT / "build" / "tools" / "wibo"
    compiler = ROOT / project.compiler
    if not wibo.is_file() or not compiler.is_file():
        fail("GHS compiler and wibo required for local fuzzy snapshot update")
    objcopy = shutil.which(project.objcopy)
    if objcopy is None:
        fallback = Path("/opt/devkitpro/devkitPPC/bin") / project.objcopy
        if not fallback.is_file():
            fail("PowerPC objcopy is unavailable for fuzzy snapshot update")
        objcopy = str(fallback)
    original_elf = ROOT / "build" / VERSION / "orig" / "RedCarpet.elf"
    for candidate in fuzzy_manifest():
        address = int(candidate["address"], 0)
        source = ROOT / candidate["source_path"]
        obj = output / (source.stem + ".o")
        binary = output / (source.stem + ".bin")
        args = ([str(wibo), str(compiler), "-c", *project.compiler_flags] +
                ["-I" + str((ROOT / include).resolve()) for include in project.include_dirs] +
                ["-o", str(obj), str(source)])
        subprocess.run(args, cwd=ROOT, check=True)
        subprocess.run([objcopy, "-O", "binary", "-j", ".text", str(obj), str(binary)],
                       cwd=ROOT, check=True)
        original = extract_elf_range(original_elf, address, candidate["size"])
        compiled = binary.read_bytes()
        if not compiled or len(compiled) % 4:
            fail("invalid compiled fuzzy PPC object")
        reference_tokens = list(opcode_tokens(original))
        compiled_tokens = list(opcode_tokens(compiled))
        matcher = SequenceMatcher(None, reference_tokens, compiled_tokens, autojunk=False)
        percent = round(matcher.ratio() * 100, 8)
        if not 0 < percent < 100:
            fail("fuzzy candidate has no measurable similarity or requires exact verification")
        results.append({"name": candidate["name"], "unit": candidate["unit"],
                        "source_path": candidate["source_path"],
                        "address": address, "size": candidate["size"],
                        "fuzzy_match_percent": percent,
                        "compiled_size": len(compiled),
                        "opcode_matches": sum(length for _, _, length in matcher.get_matching_blocks()),
                        "method": "ppc_opcode_sequence_v1"})
        print(f"Fuzzy: {candidate['name']} {percent:.2f}% opcode similarity "
              f"({len(compiled)} vs {len(original)} bytes; source C++ only)")
    return results


def create_snapshot():
    subprocess.run([sys.executable, "tools/validate_splits.py"], cwd=ROOT, check=True)
    subprocess.run(["ninja", "-j2", "progress"], cwd=ROOT, check=True)
    project, units = project_units()
    if file_sha256(ROOT / project.object) != project.sha256:
        fail("original RPX missing or SHA-256 differs from config/US/config.yml")
    report_path = ROOT / "build" / VERSION / "report.json"
    if not report_path.is_file():
        fail("run ninja -j2 progress with strict matching first")
    local_report = json.loads(report_path.read_text(encoding="utf-8"))
    records = unit_match_records(project, units)
    code_bytes = sum(item["size"] for item in records)
    if (local_report.get("code", {}).get("matched") != code_bytes
            or local_report.get("code", {}).get("total") != project.text_size
            or local_report.get("functions", {}).get("matched") != len(records)):
        fail("local report does not agree with fresh strict verification stamps; rebuild")
    if len(records) > INVENTORY_FUNCTIONS:
        fail("verified functions exceed the Ghidra inventory estimate")
    snapshot = {
        "format": 1,
        "game_version": VERSION,
        "rpx_sha256": project.sha256,
        "total_code": project.text_size,
        "data_sections": original_data_sections(ROOT / "build" / VERSION / "orig" / "RedCarpet.elf"),
        "estimated_total_functions": INVENTORY_FUNCTIONS,
        "inputs": input_hashes(),
        "matched_functions": records,
        "fuzzy_functions": measure_fuzzy(project),
    }
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Snapshot: {code_bytes:,} / {project.text_size:,} strictly matched code bytes; "
          f"{len(records)} functions")


def ratio(part, whole):
    return round(part * 100 / whole, 8) if whole else 0.0


def measures(total_code, matched_code=0, total_functions=0, matched_functions=0,
             total_units=0, complete_units=0, total_data=0, matched_data=0, fuzzy_code=0):
    percent = ratio(matched_code, total_code)
    return {
        "total_code": str(total_code),
        "matched_code": str(matched_code),
        "matched_code_percent": percent,
        "fuzzy_match_percent": ratio(matched_code + fuzzy_code, total_code),
        "complete_code": str(matched_code),
        "complete_code_percent": percent,
        "total_data": str(total_data),
        "matched_data": str(matched_data),
        "matched_data_percent": ratio(matched_data, total_data),
        "complete_data": str(matched_data),
        "complete_data_percent": ratio(matched_data, total_data),
        "total_functions": total_functions,
        "matched_functions": matched_functions,
        "matched_functions_percent": ratio(matched_functions, total_functions),
        "total_units": total_units,
        "complete_units": complete_units,
    }


def build_report():
    if not SNAPSHOT.is_file():
        fail(f"missing {SNAPSHOT.relative_to(ROOT)}: run update locally first")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    project, units = project_units()
    if snapshot.get("format") != 1 or snapshot.get("game_version") != VERSION:
        fail("unrecognized progress snapshot version")
    if snapshot.get("rpx_sha256") != project.sha256:
        fail("snapshot RPX fingerprint differs from project configuration")
    if snapshot.get("inputs") != input_hashes():
        fail("verified progress snapshot is stale; rebuild and run bytematch_report.py update")
    if snapshot.get("total_code") != project.text_size:
        fail("snapshot code size differs from project configuration")
    sections = snapshot.get("data_sections")
    if not isinstance(sections, list) or [section.get("name") for section in sections] != [".rodata", ".data"]:
        fail("snapshot initialized data sections missing or invalid")
    for section in sections:
        if (type(section.get("size")) is not int or section["size"] <= 0 or
                type(section.get("address")) is not int or section["address"] < 0):
            fail("snapshot initialized data boundaries invalid")
    data_size = sum(section["size"] for section in sections)
    estimate = snapshot.get("estimated_total_functions")
    if type(estimate) is not int or estimate < 0:
        fail("invalid estimated function inventory")
    verified = snapshot.get("matched_functions")
    if not isinstance(verified, list):
        fail("missing verified function records")
    verified_by_key = {}
    for item in verified:
        key = (item["unit"], item["name"], item["address"], item["size"])
        if key in verified_by_key:
            fail("duplicated verified function")
        verified_by_key[key] = item

    fuzzy_records = snapshot.get("fuzzy_functions", [])
    if not isinstance(fuzzy_records, list):
        fail("invalid fuzzy function records")
    manifest = fuzzy_manifest()
    if len(fuzzy_records) != len(manifest):
        fail("fuzzy records differ from configured candidates")
    fuzzy_seen = set()
    for item, candidate in zip(fuzzy_records, manifest):
        address = int(candidate["address"], 0)
        if any(item.get(key) != value for key, value in
               (("name", candidate["name"]), ("unit", candidate["unit"]),
                ("source_path", candidate["source_path"]),
                ("address", address), ("size", candidate["size"]),
                ("method", "ppc_opcode_sequence_v1"))):
            fail("fuzzy record identity differs from manifest")
        score = item.get("fuzzy_match_percent")
        compiled_size = item.get("compiled_size")
        matches = item.get("opcode_matches")
        if (type(score) not in (int, float) or not 0 < score < 100 or
                type(compiled_size) is not int or compiled_size <= 0 or
                compiled_size % 4 or type(matches) is not int or
                not 0 < matches <= min(compiled_size, item["size"]) // 4):
            fail("invalid measured fuzzy similarity")
        if (address < TEXT_BASE or address + item["size"] >
                TEXT_BASE + project.text_size):
            fail("fuzzy candidate is outside executable .text")
        extent = (address, address + item["size"])
        if any(extent[0] < end and start < extent[1] for start, end in fuzzy_seen):
            fail("overlapping fuzzy candidates")
        fuzzy_seen.add(extent)
    for unit in units:
        for section in unit.sections:
            if section.name == ".text" and any(start < section.end and section.start < end
                                               for start, end in fuzzy_seen):
                fail("fuzzy candidate overlaps an exact-matching unit")

    report_units = []
    code_assigned = 0
    matched_code = 0
    matched_functions = 0
    for unit in units:
        sections = [section for section in unit.sections if section.name == ".text"]
        code_size = sum(section.size for section in sections)
        code_assigned += code_size
        source_name = str(unit.source)
        functions = []
        code_matched = 0
        matched_count = 0
        for function in unit.functions:
            key = (unit.name, function.name, function.address, function.size)
            matched = key in verified_by_key
            if matched:
                matched_count += 1
                code_matched += function.size
                del verified_by_key[key]
            functions.append({
                "name": function.name,
                "size": str(function.size),
                "address": str(function.address - 0x02000020),
                "fuzzy_match_percent": 100.0 if matched else 0.0,
                "metadata": {"virtual_address": str(function.address)},
            })
        complete = (bool(sections) and len(sections) == len(unit.sections)
                    and code_matched == code_size)
        report_units.append({
            "name": unit.name,
            "measures": measures(code_size, code_matched, len(unit.functions), matched_count,
                                 1, int(complete)),
            "functions": functions,
            "metadata": {"complete": complete, "source_path": source_name,
                         "progress_categories": [project.progress_category]},
        })
        matched_code += code_matched
        matched_functions += matched_count
    if verified_by_key:
        fail("snapshot records do not match current tracked functions")
    if code_assigned > project.text_size:
        fail("tracked sections exceed executable text size")
    if len([fn for u in units for fn in u.functions]) > estimate:
        fail("tracked functions exceed estimated inventory")

    fuzzy_equivalent_bytes = 0.0
    for item in fuzzy_records:
        fuzzy_score = item["fuzzy_match_percent"]
        fuzzy_bytes = item["size"] * fuzzy_score / 100
        fuzzy_equivalent_bytes += fuzzy_bytes
        code_assigned += item["size"]
        report_units.append({
            "name": item["unit"],
            "measures": measures(item["size"], total_functions=1, total_units=1,
                                 fuzzy_code=fuzzy_bytes),
            "functions": [{"name": item["name"], "size": str(item["size"]),
                           "address": str(item["address"] - TEXT_BASE),
                           "fuzzy_match_percent": fuzzy_score,
                           "metadata": {"virtual_address": str(item["address"])}}],
            "metadata": {"complete": False, "source_path": item["source_path"],
                         "progress_categories": [project.progress_category]},
        })
    unmapped = project.text_size - code_assigned
    pending_functions = estimate - sum(len(unit.functions) for unit in units) - len(fuzzy_records)
    if unmapped:
        report_units.append({
            "name": "Unmapped .text (not an original object split)",
            "measures": measures(unmapped, total_functions=pending_functions, total_units=1),
            "metadata": {"complete": False,
                         "progress_categories": [project.progress_category]},
        })
    report_units.append({
        "name": "Unmapped initialized data (.rodata + .data)",
        "measures": measures(0, total_data=data_size, total_units=1),
        "metadata": {"complete": False,
                     "progress_categories": [project.progress_category]},
    })
    complete_units = sum(int(unit["metadata"]["complete"]) for unit in report_units)
    report_measures = measures(project.text_size, matched_code, estimate, matched_functions,
                               len(report_units), complete_units, total_data=data_size,
                               fuzzy_code=fuzzy_equivalent_bytes)
    report = {
        "version": 2,
        "measures": report_measures,
        "units": report_units,
        "categories": [{"id": project.progress_category,
                        "name": project.progress_category_name,
                        "measures": report_measures}],
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Generate verified ByteMatch objdiff v2 progress")
    parser.add_argument("mode", choices=("update", "generate", "check"))
    args = parser.parse_args()
    try:
        if args.mode == "update":
            create_snapshot()
        report = build_report()
        encoded = json.dumps(report, indent=2) + "\n"
        if args.mode == "check":
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != encoded:
                fail("ByteMatch report missing or out of date; run generate")
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(encoded, encoding="utf-8")
        matched = report["measures"]["matched_code"]
        total = report["measures"]["total_code"]
        print(f"ByteMatch: {matched} / {total} bytes "
              f"({report['measures']['matched_code_percent']:.6f}%) -> {OUTPUT.relative_to(ROOT)}")
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"bytematch: {error}\n")


if __name__ == "__main__":
    main()
