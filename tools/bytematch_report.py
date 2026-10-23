#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from configure import (
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
INVENTORY_FUNCTIONS = 30941


def fail(message):
    raise ValueError(message)


def input_hashes():
    files = [ROOT / "configure.py", ROOT / "CMakeLists.txt", ROOT / "tools" / "validate_splits.py"]
    for directory in (ROOT / "config" / VERSION, ROOT / "src", ROOT / "include"):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and path != SNAPSHOT and "__pycache__" not in path.parts)
    return {str(path.relative_to(ROOT)): file_sha256(path)
            for path in sorted(files)}


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
        "estimated_total_functions": INVENTORY_FUNCTIONS,
        "inputs": input_hashes(),
        "matched_functions": records,
    }
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Snapshot: {code_bytes:,} / {project.text_size:,} strictly matched code bytes; "
          f"{len(records)} functions")


def ratio(part, whole):
    return round(part * 100 / whole, 8) if whole else 0.0


def measures(total_code, matched_code=0, total_functions=0, matched_functions=0,
             total_units=0, complete_units=0):
    percent = ratio(matched_code, total_code)
    return {
        "total_code": str(total_code),
        "matched_code": str(matched_code),
        "matched_code_percent": percent,
        "fuzzy_match_percent": percent,
        "complete_code": str(matched_code),
        "complete_code_percent": percent,
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

    unmapped = project.text_size - code_assigned
    pending_functions = estimate - sum(len(unit.functions) for unit in units)
    if unmapped:
        report_units.append({
            "name": "Unmapped .text (not an original object split)",
            "measures": measures(unmapped, total_functions=pending_functions, total_units=1),
            "metadata": {"complete": False,
                         "progress_categories": [project.progress_category]},
        })
    complete_units = sum(int(unit["metadata"]["complete"]) for unit in report_units)
    report_measures = measures(project.text_size, matched_code, estimate, matched_functions,
                               len(report_units), complete_units)
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
