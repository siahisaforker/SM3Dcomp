#!/usr/bin/env python3

"""
Generate the matching decompilation build.

The user-facing workflow intentionally follows the decomp-toolkit project
convention:

    python3 configure.py
    ninja
    ninja progress

The backend is RPX-specific because decomp-toolkit does not support Wii U RPX
files. Generated objects are compiled with GHS through wibo/Wine on non-Windows
hosts, linked at their original addresses, and compared byte-for-byte with the
corresponding RPX ranges.
"""

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_VERSION = "US"
VERSIONS = ("US",)
WIBO_TAG = "1.2.0"


@dataclass(frozen=True)
class Symbol:
    name: str
    section: str
    address: int
    size: int | None


@dataclass(frozen=True)
class SectionRange:
    name: str
    start: int
    end: int

    @property
    def size(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class Function:
    name: str
    address: int
    size: int


@dataclass(frozen=True)
class Unit:
    name: str
    source: str
    sections: tuple[SectionRange, ...]
    functions: tuple[Function, ...]


@dataclass(frozen=True)
class ProjectConfig:
    object: Path
    sha256: str
    text_size: int
    symbols: Path
    splits: Path
    undefined_maps: tuple[Path, ...]
    import_maps: tuple[Path, ...]
    source_dir: Path
    compiler: str
    compiler_flags: tuple[str, ...]
    include_dirs: tuple[Path, ...]
    linker: str
    linker_flags: tuple[str, ...]
    objcopy: str
    objcopy_extract_flags: tuple[str, ...]
    progress_category: str
    progress_category_name: str


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        sys.exit("configure.py requires PyYAML (python -m pip install PyYAML)")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        sys.exit(f"{path}: invalid YAML: {error}")
    if not isinstance(value, dict):
        sys.exit(f"{path}: expected a YAML mapping")
    return value


def config_value(values: dict[str, Any], path: Path, key: str) -> Any:
    if key not in values:
        sys.exit(f"{path}: missing {key}")
    return values[key]


def config_string(values: dict[str, Any], path: Path, key: str) -> str:
    value = config_value(values, path, key)
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        sys.exit(f"{path}: {key} must be a string")
    return str(value)


def config_int(values: dict[str, Any], path: Path, key: str) -> int:
    value = config_value(values, path, key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError:
            pass
    sys.exit(f"{path}: {key} must be an integer")


def config_list(values: dict[str, Any], path: Path, key: str) -> tuple[str, ...]:
    value = config_value(values, path, key)
    if isinstance(value, str):
        try:
            return tuple(shlex.split(value, posix=os.name != "nt"))
        except ValueError as error:
            sys.exit(f"{path}: invalid {key}: {error}")
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        sys.exit(f"{path}: {key} must be a string or list of strings")
    return tuple(value)


def config_optional_paths(values: dict[str, Any], path: Path, key: str) -> tuple[Path, ...]:
    if key not in values:
        return ()
    value = values[key]
    if isinstance(value, str):
        return (Path(value),)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        sys.exit(f"{path}: {key} must be a string or list of strings")
    return tuple(Path(item) for item in value)


def load_project(root: Path, version: str) -> ProjectConfig:
    path = root / "config" / version / "config.yml"
    if not path.is_file():
        sys.exit(f"unknown version {version}: missing {path}")
    values = load_yaml(path)
    undefined_maps = tuple(
        Path(config_string(values, path, key))
        for key in ("undefined_funcs", "undefined_syms")
    )
    return ProjectConfig(
        object=Path(config_string(values, path, "object")),
        sha256=config_string(values, path, "sha256").lower(),
        text_size=config_int(values, path, "text_size"),
        symbols=Path(config_string(values, path, "symbols")),
        splits=Path(config_string(values, path, "splits")),
        undefined_maps=undefined_maps,
        import_maps=config_optional_paths(values, path, "import_maps"),
        source_dir=Path(config_string(values, path, "source_dir")),
        compiler=config_string(values, path, "compiler"),
        compiler_flags=config_list(values, path, "compiler_flags"),
        include_dirs=tuple(Path(item) for item in config_list(values, path, "include_dirs")),
        linker=config_string(values, path, "linker"),
        linker_flags=config_list(values, path, "linker_flags"),
        objcopy=config_string(values, path, "objcopy"),
        objcopy_extract_flags=config_list(values, path, "objcopy_extract_flags"),
        progress_category=config_string(values, path, "progress_category"),
        progress_category_name=config_string(values, path, "progress_category_name"),
    )


def strip_comment(line: str) -> str:
    positions = [position for marker in ("//", "#")
                 if (position := line.find(marker)) >= 0]
    return line[:min(positions)] if positions else line


def parse_number(text: str, path: Path, number: int) -> int:
    try:
        return int(text, 0)
    except ValueError:
        sys.exit(f"{path}:{number}: invalid integer {text}")


def load_symbols(path: Path) -> tuple[Symbol, ...]:
    pattern = re.compile(
        r"^(?P<name>[^=\s]+)\s*=\s*(?P<section>\.[A-Za-z0-9_.$]+):"
        r"(?P<address>0[xX][0-9a-fA-F]+|[0-9]+)\s*;\s*$"
    )
    size_pattern = re.compile(r"\bsize\s*:\s*(0[xX][0-9a-fA-F]+|[0-9]+)\b")
    symbols: list[Symbol] = []
    names: set[str] = set()
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        comment_at = raw_line.find("//")
        comment = raw_line[comment_at + 2:] if comment_at >= 0 else ""
        line = strip_comment(raw_line).strip()
        if not line:
            continue
        match = pattern.match(line)
        if not match:
            sys.exit(f"{path}:{number}: invalid symbol")
        name = match.group("name")
        if name in names:
            sys.exit(f"{path}:{number}: duplicate symbol {name}")
        names.add(name)
        size_match = size_pattern.search(comment)
        symbols.append(Symbol(
            name=name,
            section=match.group("section"),
            address=parse_number(match.group("address"), path, number),
            size=parse_number(size_match.group(1), path, number) if size_match else None,
        ))
    return tuple(symbols)


def load_undefined_maps(root: Path, paths: tuple[Path, ...]) -> dict[str, int]:
    pattern = re.compile(
        r"^(?P<name>[^=\s]+)\s*=\s*"
        r"(?P<address>0[xX][0-9a-fA-F]+|[0-9]+)\s*;?\s*$"
    )
    values: dict[str, int] = {}
    for relative_path in paths:
        path = root / relative_path
        for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = strip_comment(raw_line).strip()
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                sys.exit(f"{path}:{number}: invalid undefined symbol")
            name = match.group("name")
            address = parse_number(match.group("address"), path, number)
            if name in values and values[name] != address:
                sys.exit(f"{path}:{number}: conflicting address for {name}")
            values[name] = address
    return values


def load_units(root: Path, project: ProjectConfig,
               symbols: tuple[Symbol, ...]) -> tuple[Unit, ...]:
    section_pattern = re.compile(
        r"^(?P<section>\.[A-Za-z0-9_.$]+)\s+"
        r"start\s*:\s*(?P<start>0[xX][0-9a-fA-F]+|[0-9]+)\s+"
        r"end\s*:\s*(?P<end>0[xX][0-9a-fA-F]+|[0-9]+)\s*$"
    )
    split_path = root / project.splits
    raw_units: list[tuple[str, list[SectionRange]]] = []
    current_source: str | None = None
    current_sections: list[SectionRange] | None = None
    for number, raw_line in enumerate(split_path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_comment(raw_line).strip()
        if not line:
            continue
        if not raw_line[:1].isspace() and line.endswith(":"):
            current_source = line[:-1].strip()
            if not current_source:
                sys.exit(f"{split_path}:{number}: empty unit name")
            current_sections = []
            raw_units.append((current_source, current_sections))
            continue
        match = section_pattern.match(line)
        if current_source is None or current_sections is None or not match:
            sys.exit(f"{split_path}:{number}: invalid split")
        section = SectionRange(
            match.group("section"),
            parse_number(match.group("start"), split_path, number),
            parse_number(match.group("end"), split_path, number),
        )
        if section.end <= section.start:
            sys.exit(f"{split_path}:{number}: split end must be after start")
        if any(item.name == section.name for item in current_sections):
            sys.exit(f"{split_path}:{number}: duplicate {section.name} split")
        current_sections.append(section)

    occupied: dict[str, list[tuple[int, int, str]]] = {}
    for source, sections in raw_units:
        for section in sections:
            for previous_start, previous_end, previous_source in occupied.get(section.name, []):
                if section.start < previous_end and section.end > previous_start:
                    sys.exit(f"{split_path}: overlapping {section.name} ranges: "
                             f"{previous_source} and {source}")
            occupied.setdefault(section.name, []).append((section.start, section.end, source))

    units: list[Unit] = []
    assigned_functions: set[str] = set()
    for source, sections in raw_units:
        if not sections:
            sys.exit(f"{split_path}: {source} has no sections")
        source_relative = Path(source)
        if source_relative.parts[:len(project.source_dir.parts)] != project.source_dir.parts:
            source_relative = project.source_dir / source_relative
        if not (root / source_relative).is_file():
            sys.exit(f"missing source file {source_relative}")
        text_ranges = [section for section in sections if section.name == ".text"]
        functions = sorted(
            (Function(symbol.name, symbol.address, symbol.size)
             for symbol in symbols
             if symbol.section == ".text" and symbol.size is not None
             and any(section.start <= symbol.address
                     and symbol.address + symbol.size <= section.end
                     for section in text_ranges)),
            key=lambda function: function.address,
        )
        for function in functions:
            if function.name in assigned_functions:
                sys.exit(f"{split_path}: function {function.name} is in multiple units")
            assigned_functions.add(function.name)
        try:
            name_path = source_relative.relative_to(project.source_dir)
        except ValueError:
            name_path = source_relative
        units.append(Unit(
            name=name_path.with_suffix("").as_posix(),
            source=source_relative.as_posix(),
            sections=tuple(sections),
            functions=tuple(functions),
        ))
    if not units:
        sys.exit(f"{split_path}: no units")
    unassigned = [symbol.name for symbol in symbols
                  if symbol.section == ".text" and symbol.size is not None
                  and symbol.name not in assigned_functions]
    if unassigned:
        sys.exit(f"text symbols not covered by splits: {', '.join(unassigned)}")
    return tuple(units)


def slash(path: Path) -> str:
    return path.as_posix()


def ninja_escape(value: str) -> str:
    return value.replace("$", "$$").replace(" ", "$ ").replace(":", "$:")


def quote(value: str | Path) -> str:
    return f'"{value}"'


def shell_args(values: tuple[str, ...]) -> str:
    return " ".join(quote(value) if any(char.isspace() for char in value) else value
                    for value in values)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_elf_range(input_path: Path, address: int, size: int) -> bytes:
    data = input_path.read_bytes()
    if len(data) < 52 or data[:7] != b"\x7fELF\x01\x02\x01":
        sys.exit(f"{input_path}: expected a big-endian ELF32 file")
    elf_type, machine = struct.unpack_from(">HH", data, 16)
    if elf_type != 0xFE01 or machine != 20:
        sys.exit(f"{input_path}: expected a decompressed Wii U PowerPC RPX/RPL")
    section_offset = struct.unpack_from(">I", data, 32)[0]
    section_size, section_count = struct.unpack_from(">HH", data, 46)
    if section_size != 40 or section_offset + section_size * section_count > len(data):
        sys.exit(f"{input_path}: invalid section table")
    if address < 0 or size < 0 or address + size > 0x100000000:
        sys.exit("ELF extraction range is outside the 32-bit address space")

    for index in range(section_count):
        header = section_offset + index * section_size
        section_type, flags, section_address, file_offset, file_size = struct.unpack_from(
            ">IIIII", data, header + 4
        )
        if not (section_address <= address
                and address + size <= section_address + file_size):
            continue
        if section_type == 8:
            sys.exit(f"{input_path}: address 0x{address:08x} has no file data")
        if flags & 0x08000000:
            sys.exit(
                f"{input_path}: section {index} is still compressed; "
                "run wiiurpxtool -d first"
            )
        if file_offset + file_size > len(data):
            sys.exit(f"{input_path}: section {index} is outside the file")
        relative = address - section_address
        return data[file_offset + relative:file_offset + relative + size]
    sys.exit(f"{input_path}: address 0x{address:08x} is not mapped")


def install_original(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    try:
        os.link(source, destination)
        print(f"linked {destination} -> {source}")
    except OSError:
        shutil.copy2(source, destination)
        print(f"copied {source} -> {destination}")


def files_under(path: Path, suffixes: tuple[str, ...] | None = None) -> list[Path]:
    if not path.is_dir():
        return []
    skipped = {"build", ".git", ".local", "__pycache__"}
    return sorted(file for file in path.rglob("*")
                  if file.is_file()
                  and not any(part in skipped for part in file.parts)
                  and (suffixes is None or file.suffix.lower() in suffixes))


def write_if_changed(path: Path, text: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def resolve_tool(root: Path, configured: str, description: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(configured))
    candidate = Path(expanded)
    if candidate.is_absolute() or candidate.parent != Path("."):
        candidate = candidate if candidate.is_absolute() else root / candidate
        resolved = candidate.resolve()
        if resolved.is_file():
            return resolved
    else:
        found = shutil.which(expanded)
        if found:
            return Path(found).resolve()
        fallback_dirs = []
        if devkitppc := os.environ.get("DEVKITPPC"):
            fallback_dirs.append(Path(devkitppc) / "bin")
        if devkitpro := os.environ.get("DEVKITPRO"):
            fallback_dirs.append(Path(devkitpro) / "devkitPPC" / "bin")
        fallback_dirs.append(Path("/opt/devkitpro/devkitPPC/bin"))
        for directory in fallback_dirs:
            fallback = directory / expanded
            if fallback.is_file():
                return fallback.resolve()
    sys.exit(f"{description} is missing: {configured}")


def compiler_wrapper(root: Path, args: argparse.Namespace) -> tuple[Path | None, bool]:
    if os.name == "nt":
        return None, False
    if args.wrapper:
        return resolve_tool(root, str(args.wrapper), "compiler wrapper"), False
    return (root / args.build_dir / "tools" / "wibo").resolve(), True


def section_tag(section: str) -> str:
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", section.lstrip("."))
    return tag or "section"


def unit_paths(build_root: Path, project: ProjectConfig, unit: Unit) -> dict[str, Path]:
    return {
        "object": build_root / project.source_dir / f"{unit.name}.o",
        "script": build_root / "ld" / f"{unit.name}.ld",
        "linked": build_root / "linked" / f"{unit.name}.elf",
        "base": build_root / "orig" / f"{unit.name}.o",
    }


def verification_paths(build_root: Path, unit: Unit,
                       section: SectionRange) -> dict[str, Path]:
    tag = section_tag(section.name)
    return {
        "actual": build_root / "verify" / "actual" / unit.name / f"{tag}.bin",
        "expected": build_root / "verify" / "expected" / unit.name / f"{tag}.bin",
        "stamp": build_root / "verify" / "stamps" / unit.name / f"{tag}.ok",
    }


def linker_script(unit: Unit, undefined: dict[str, int]) -> str:
    lines = ["/* Generated by configure.py. */"]
    lines.extend(f"{name} = 0x{address:08x};" for name, address in sorted(undefined.items()))
    lines.extend(["", "SECTIONS", "{"])
    for section in unit.sections:
        lines.extend([
            f"  {section.name} 0x{section.start:08x} :",
            "  {",
            f"    *({section.name})",
            f"    *({section.name}.*)",
            "  }",
            f"  ASSERT(SIZEOF({section.name}) == 0x{section.size:x}, "
            f'"{unit.name} {section.name} size mismatch")',
            "",
        ])
    lines.extend(["  /DISCARD/ : { *(*) }", "}", ""])
    return "\n".join(lines)


def relative_to_root(root: Path, path: Path) -> str:
    return slash(path.resolve().relative_to(root))


def build_input(root: Path, path: Path) -> str:
    try:
        value = relative_to_root(root, path)
    except ValueError:
        value = slash(path.resolve())
    return ninja_escape(value)


def configure(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parent
    project = load_project(root, args.version)
    symbols = load_symbols(root / project.symbols)
    undefined = load_undefined_maps(root, project.undefined_maps + project.import_maps)
    units = load_units(root, project, symbols)
    build_root = (root / args.build_dir / args.version).resolve()
    try:
        build_root.relative_to(root)
    except ValueError:
        sys.exit("--build-dir must be inside the repository")
    original = root / project.object
    if args.rpx:
        install_original(args.rpx, original)
    if not original.is_file():
        sys.exit(f"missing {original}\nrun configure.py --rpx <path-to-RedCarpet.rpx>")
    actual_hash = file_sha256(original)
    if actual_hash != project.sha256:
        sys.exit(f"wrong RPX hash: {actual_hash}")

    compiler = resolve_tool(root, str(args.compiler) if args.compiler else project.compiler,
                            "compiler")
    wrapper, download_wrapper = compiler_wrapper(root, args)
    linker_name = Path(project.linker).name
    objcopy_name = Path(project.objcopy).name
    linker_config = str(args.binutils / linker_name) if args.binutils else project.linker
    objcopy_config = str(args.binutils / objcopy_name) if args.binutils else project.objcopy
    linker = resolve_tool(root, linker_config, "linker")
    objcopy = resolve_tool(root, objcopy_config, "objcopy")
    if args.wiiurpxtool:
        wiiurpxtool = resolve_tool(root, str(args.wiiurpxtool), "wiiurpxtool")
        build_wiiurpx = False
    else:
        executable = "wiiurpxtool.exe" if os.name == "nt" else "wiiurpxtool"
        wiiurpxtool = (
            root / args.build_dir / "tools" / "wiiurpxtool" / executable
        ).resolve()
        build_wiiurpx = True
    paths_by_unit = [(unit, unit_paths(build_root, project, unit)) for unit in units]
    for unit, paths in paths_by_unit:
        write_if_changed(paths["script"], linker_script(unit, undefined))

    header_files: list[Path] = []
    for include_dir in project.include_dirs:
        header_files.extend(files_under(root / include_dir,
                                        (".h", ".hh", ".hpp", ".hxx", ".inc")))
    header_files = sorted(set(header_files))
    download_tool = root / "tools" / "download_tool.py"
    wiiurpx_sources = [
        root / "CMakeLists.txt",
        *files_under(root / "tools" / "wiiurpxtool"),
        *files_under(root / "tools" / "wiiurpxtool-compat"),
    ]
    decompressed_rpx = build_root / "orig" / "RedCarpet.elf"
    config_inputs = [Path("configure.py"), *(
        path.relative_to(root) for path in files_under(root / "config" / args.version)
    )]

    build_dir = slash(args.build_dir)
    reconfigure = ["$python", "configure.py", "configure", "--version", args.version,
                   "--build-dir", build_dir]
    if args.compiler:
        reconfigure.extend(["--compiler", quote(compiler)])
    if args.wrapper:
        reconfigure.extend(["--wrapper", quote(wrapper)])
    if args.wiiurpxtool:
        reconfigure.extend(["--wiiurpxtool", quote(wiiurpxtool)])
    if args.binutils:
        reconfigure.extend(["--binutils", quote(args.binutils.resolve())])
    if args.non_matching:
        reconfigure.append("--non-matching")
    if not args.progress:
        reconfigure.append("--no-progress")
    if args.verbose:
        reconfigure.append("--verbose")
    progress_command = ("$python configure.py progress --version " + args.version +
                        " --build-dir " + build_dir)
    if args.verbose:
        progress_command += " --verbose"
    compiler_command = " ".join(
        part for part in (quote(wrapper) if wrapper else "", quote(compiler)) if part
    )
    include_flags = tuple(
        f"-I{(root / include_dir).resolve()}" for include_dir in project.include_dirs
    )
    verify_flags = " --non-matching" if args.non_matching else ""
    lines = [
        "ninja_required_version = 1.10",
        f"python = {quote(Path(sys.executable).resolve())}",
        f"compiler = {compiler_command}",
        f"compiler_flags = {shell_args(project.compiler_flags)}",
        f"includes = {shell_args(include_flags)}",
        f"linker = {quote(linker)}",
        f"linker_flags = {shell_args(project.linker_flags)}",
        f"objcopy = {quote(objcopy)}",
        f"objcopy_extract_flags = {shell_args(project.objcopy_extract_flags)}",
        f"wiiurpxtool = {quote(wiiurpxtool)}",
        f"reference_elf = {quote(decompressed_rpx)}",
        "",
        "rule configure",
        "  command = " + " ".join(reconfigure),
        "  description = configure",
        "  generator = 1",
        "  restat = 1",
        "",
        "rule download_tool",
        "  command = $python tools/download_tool.py $tool $out --tag $tag",
        "  description = download $tool",
        "",
        "rule build_wiiurpxtool",
        "  command = cmake -S . -B " + build_dir +
        "/tools/wiiurpxtool -G Ninja -DCMAKE_BUILD_TYPE=Release && "
        "cmake --build " + build_dir +
        "/tools/wiiurpxtool --target wiiurpxtool",
        "  description = build wiiurpxtool",
        "  pool = console",
        "  restat = 1",
        "",
        "rule decompress_rpx",
        "  command = $wiiurpxtool -d $in $out",
        "  description = decompress $in",
        "",
        "rule compile",
        "  command = $compiler -c $compiler_flags $includes -o $out $in",
        "  description = compile $in",
        "",
        "rule link_unit",
        "  command = $linker $linker_flags -T $script -o $out $in",
        "  description = link $name",
        "",
        "rule extract_actual",
        "  command = $objcopy $objcopy_extract_flags --only-section $section $in $out",
        "  description = extract linked $name $section",
        "",
        "rule extract_expected",
        "  command = $python configure.py extract --input $reference_elf "
        "--address $address --size $size --output $out",
        "  description = extract original $name $section",
        "",
        "rule verify",
        "  command = $python configure.py verify --actual $actual --expected $expected "
        "--stamp $out --object $verify_object --source $verify_source "
        "--script $verify_script --section-start $section_start --section-end $section_end" +
        verify_flags,
        "  description = verify $name $section",
        "",
        "rule make_base",
        "  command = $python configure.py make-base --object $object --output $out $sections",
        "  description = make objdiff base $name",
        "",
        "rule report_progress",
        "  command = " + progress_command,
        "  description = progress",
        "  restat = 1",
        "",
    ]

    generated = [root / "build.ninja", root / "objdiff.json",
                 root / "compile_commands.json",
                 *(paths["script"] for _, paths in paths_by_unit)]
    lines.append(
        "build " + " ".join(build_input(root, path) for path in generated) +
        ": configure " + " ".join(ninja_escape(slash(path)) for path in config_inputs)
    )
    if download_wrapper and wrapper is not None:
        lines.extend([
            "build " + build_input(root, wrapper) + ": download_tool " +
            build_input(root, download_tool),
            "  tool = wibo",
            f"  tag = {WIBO_TAG}",
        ])
    if build_wiiurpx:
        lines.append(
            "build " + build_input(root, wiiurpxtool) + ": build_wiiurpxtool " +
            " ".join(build_input(root, path) for path in wiiurpx_sources)
        )
    lines.append(
        "build " + build_input(root, decompressed_rpx) + ": decompress_rpx " +
        build_input(root, original) + " | " + build_input(root, wiiurpxtool)
    )
    object_paths = [paths["object"] for _, paths in paths_by_unit]
    compiler_inputs = [compiler, *([wrapper] if wrapper else [])]
    for unit, paths in paths_by_unit:
        lines.append(
            "build " + build_input(root, paths["object"]) + ": compile " +
            build_input(root, root / unit.source) + " | " +
            " ".join(build_input(root, path) for path in header_files + compiler_inputs)
        )

    verify_stamps: list[Path] = []
    base_objects: list[Path] = []
    for unit, paths in paths_by_unit:
        lines.extend([
            "build " + build_input(root, paths["linked"]) + ": link_unit " +
            build_input(root, paths["object"]) + " | " + build_input(root, paths["script"]) +
            " " + build_input(root, linker),
            "  script = " + quote(paths["script"]),
            f"  name = {unit.name}",
        ])
        expected_bins: list[Path] = []
        for section in unit.sections:
            verify_paths = verification_paths(build_root, unit, section)
            actual = verify_paths["actual"]
            expected = verify_paths["expected"]
            stamp = verify_paths["stamp"]
            expected_bins.append(expected)
            verify_stamps.append(stamp)
            lines.extend([
                "build " + build_input(root, actual) + ": extract_actual " +
                build_input(root, paths["linked"]) + " | " + build_input(root, objcopy),
                f"  section = {section.name}",
                f"  name = {unit.name}",
                "build " + build_input(root, expected) + ": extract_expected " +
                build_input(root, decompressed_rpx) +
                " || " + build_input(root, paths["object"]),
                f"  address = 0x{section.start:08x}",
                f"  size = 0x{section.size:x}",
                f"  section = {section.name}",
                f"  name = {unit.name}",
                "build " + build_input(root, stamp) + ": verify " +
                build_input(root, actual) + " " + build_input(root, expected),
                "  actual = " + quote(actual),
                "  expected = " + quote(expected),
                "  verify_object = " + quote(paths["object"]),
                "  verify_source = " + quote((root / unit.source).resolve()),
                "  verify_script = " + quote(paths["script"]),
                f"  section_start = 0x{section.start:08x}",
                f"  section_end = 0x{section.end:08x}",
                f"  section = {section.name}",
                f"  name = {unit.name}",
            ])
        base_objects.append(paths["base"])
        base_sections = " ".join(
            "--section " + quote(section.name + "|" + str(
                verification_paths(build_root, unit, section)["actual"]) + "|" +
                str(expected))
            for section, expected in zip(unit.sections, expected_bins)
        )
        lines.extend([
            "build " + build_input(root, paths["base"]) + ": make_base " +
            build_input(root, paths["object"]) + " " +
            " ".join(build_input(root, verification_paths(build_root, unit, section)["actual"])
                     for section in unit.sections) + " " +
            " ".join(build_input(root, path) for path in expected_bins),
            "  object = " + quote(paths["object"]),
            "  sections = " + base_sections,
            f"  name = {unit.name}",
        ])

    report_json = build_root / "report.json"
    lines.append(
        "build " + build_input(root, report_json) + ": report_progress " +
        " ".join(build_input(root, path) for path in verify_stamps)
    )
    tools = [*([wrapper] if wrapper else []), wiiurpxtool]
    lines.append("build tools: phony " +
                 " ".join(build_input(root, path) for path in tools))
    lines.append("build all_source: phony " +
                 " ".join(build_input(root, path) for path in object_paths + base_objects))
    lines.append("build verify: phony " +
                 " ".join(build_input(root, path) for path in verify_stamps))
    lines.append("build progress: phony " + build_input(root, report_json))
    default_inputs = ["all_source", *(["progress"] if args.progress else [])]
    lines.append("build all: phony " + " ".join(default_inputs))
    lines.append("default all")
    write_if_changed(root / "build.ninja", "\n".join(lines) + "\n")

    watch_patterns = [
        "configure.py",
        f"config/{args.version}/**/*",
        f"{slash(project.source_dir)}/**/*",
        *(f"{slash(path)}/**/*" for path in project.include_dirs),
        "CMakeLists.txt",
        "tools/download_tool.py",
        "tools/wiiurpxtool/**/*",
        "tools/wiiurpxtool-compat/**/*",
    ]
    existing_units: dict[str, dict[str, Any]] = {}
    objdiff_path = root / "objdiff.json"
    if objdiff_path.is_file():
        try:
            existing = json.loads(objdiff_path.read_text(encoding="utf-8"))
            existing_units = {
                unit["name"]: unit
                for unit in existing.get("units", [])
                if isinstance(unit, dict) and isinstance(unit.get("name"), str)
            }
        except (json.JSONDecodeError, OSError):
            pass

    def objdiff_unit(unit: Unit, paths: dict[str, Path]) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": unit.name,
            "target_path": relative_to_root(root, paths["object"]),
            "base_path": relative_to_root(root, paths["base"]),
            "metadata": {
                # A source-backed split is the RPX equivalent of Object(Matching)
                # in a decomp-toolkit project.
                "complete": True,
                "source_path": unit.source,
                "progress_categories": [project.progress_category],
            },
        }
        mappings = existing_units.get(unit.name, {}).get("symbol_mappings")
        if mappings:
            result["symbol_mappings"] = mappings
        return result

    objdiff = {
        "min_version": "2.0.0-beta.5",
        "custom_make": "ninja",
        "build_target": False,
        "watch_patterns": list(dict.fromkeys(watch_patterns)),
        "units": [objdiff_unit(unit, paths) for unit, paths in paths_by_unit],
        "progress_categories": [{"id": project.progress_category,
                                 "name": project.progress_category_name}],
    }
    write_if_changed(objdiff_path, json.dumps(objdiff, indent=2) + "\n")

    compiler_arguments = ([str(wrapper)] if wrapper else []) + [str(compiler)]
    compile_commands = [
        {
            "directory": str(root),
            "file": str((root / unit.source).resolve()),
            "output": str(paths["object"]),
            "arguments": [*compiler_arguments, "-c", *project.compiler_flags,
                          *(f"-I{(root / include_dir).resolve()}"
                            for include_dir in project.include_dirs),
                          "-o", str(paths["object"]), str((root / unit.source).resolve())],
        }
        for unit, paths in paths_by_unit
    ]
    write_if_changed(root / "compile_commands.json", json.dumps(compile_commands, indent=2) + "\n")
    print(f"configured {args.version}: {len(units)} unit, "
          f"{sum(len(unit.functions) for unit in units)} functions, "
          f"{sum(len(unit.sections) for unit in units)} sections")


def is_verification_fresh(root: Path, build_root: Path, project: ProjectConfig,
                          unit: Unit, section: SectionRange,
                          undefined: dict[str, int]) -> bool:
    paths = unit_paths(build_root, project, unit)
    verify_paths = verification_paths(build_root, unit, section)
    required = [paths["object"], paths["script"], paths["linked"],
                *verify_paths.values(), root / project.object,
                root / unit.source]
    if not all(path.is_file() for path in required):
        return False
    if paths["script"].read_text(encoding="utf-8") != linker_script(unit, undefined):
        return False
    actual_hash = file_sha256(verify_paths["actual"])
    expected_hash = file_sha256(verify_paths["expected"])
    if actual_hash != expected_hash:
        return False
    try:
        stamp = json.loads(verify_paths["stamp"].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Stamps made before versioned verification records still represent a
        # byte-for-byte match. Source edits remain stale until they are rebuilt.
        return ((root / unit.source).stat().st_mtime_ns <=
                paths["object"].stat().st_mtime_ns)
    if not isinstance(stamp, dict) or stamp.get("version") not in (1, 2):
        return False
    return (
        stamp.get("matched", True) is True
        and stamp.get("section_start") == section.start
        and stamp.get("section_end") == section.end
        and stamp.get("actual_sha256") == actual_hash
        and stamp.get("expected_sha256") == expected_hash
        and stamp.get("object_sha256") == file_sha256(paths["object"])
        and stamp.get("source_sha256") == file_sha256(root / unit.source)
    )


def progress(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parent
    project = load_project(root, args.version)
    symbols = load_symbols(root / project.symbols)
    undefined = load_undefined_maps(root, project.undefined_maps + project.import_maps)
    units = load_units(root, project, symbols)
    build_root = (root / args.build_dir / args.version).resolve()
    fresh_sections = {
        (unit.name, section.name)
        for unit in units for section in unit.sections
        if is_verification_fresh(root, build_root, project, unit, section,
                                 undefined)
    }
    functions = [function for unit in units for function in unit.functions]
    matched = [function for unit in units for function in unit.functions
               if (unit.name, ".text") in fresh_sections]
    matched_bytes = sum(function.size for function in matched)
    complete_units = sum(
        all((unit.name, section.name) in fresh_sections for section in unit.sections)
        for unit in units
    )
    percent = matched_bytes / project.text_size * 100
    measures = {
        "matched_code": matched_bytes,
        "total_code": project.text_size,
        "matched_code_percent": percent,
        "matched_functions": len(matched),
        "total_functions": len(functions),
        "complete_units": complete_units,
        "total_units": len(units),
    }
    report = {
        "version": args.version,
        "measures": measures,
        "categories": [{
            "id": project.progress_category,
            "name": project.progress_category_name,
            "measures": measures,
        }],
        "code": {"matched": matched_bytes, "total": project.text_size,
                 "percent": percent},
        "functions": {"matched": len(matched), "tracked": len(functions)},
        "sections": {"matched": len(fresh_sections),
                     "tracked": sum(len(unit.sections) for unit in units)},
        "units": {"complete": complete_units, "total": len(units)},
    }
    report_path = build_root / "report.json"
    write_if_changed(report_path, json.dumps(report, indent=2) + "\n")
    report_path.touch()
    print("Progress:")
    print(f"  {project.progress_category_name}: {percent:.4f}% matched "
          f"({complete_units} / {len(units)} tracked files)")
    print(f"    Code: {matched_bytes:,} / {project.text_size:,} bytes "
          f"({len(matched)} / {len(functions)} tracked functions)")
    print(f"    Sections: {len(fresh_sections)} / {report['sections']['tracked']}")
    if args.verbose:
        for unit in units:
            matched_unit = all(
                (unit.name, section.name) in fresh_sections for section in unit.sections
            )
            print(f"    {'MATCH' if matched_unit else 'MISSING'} {unit.name}")


def verify(args: argparse.Namespace) -> None:
    required = (args.actual, args.expected, args.stamp, args.object,
                args.source, args.script, args.section_start, args.section_end)
    if any(value is None for value in required):
        sys.exit("verify requires actual, expected, stamp, object, source, script, and section bounds")
    args.stamp.unlink(missing_ok=True)
    actual = args.actual.read_bytes()
    expected = args.expected.read_bytes()
    matched = actual == expected
    first: int | None = None
    if not matched:
        first = next((index for index, pair in enumerate(zip(actual, expected))
                      if pair[0] != pair[1]), min(len(actual), len(expected)))
        message = (f"verification failed: {args.actual} differs from {args.expected} "
                   f"at offset 0x{first:x} ({len(actual)} vs {len(expected)} bytes)")
        if not args.non_matching:
            sys.exit(message)
        print("warning: " + message, file=sys.stderr)
    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "version": 2,
        "matched": matched,
        "section_start": args.section_start,
        "section_end": args.section_end,
        "actual_sha256": hashlib.sha256(actual).hexdigest(),
        "expected_sha256": hashlib.sha256(expected).hexdigest(),
        "object_sha256": file_sha256(args.object),
        "source_sha256": file_sha256(args.source),
    }
    if first is not None:
        record["first_difference"] = first
    args.stamp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def extract(args: argparse.Namespace) -> None:
    if args.input is None or args.address is None or args.size is None or args.output is None:
        sys.exit("extract requires --input, --address, --size, and --output")
    data = extract_elf_range(args.input, args.address, args.size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)


def make_base(args: argparse.Namespace) -> None:
    if args.object is None or args.output is None or not args.section:
        sys.exit("make-base requires --object, --output, and --section")
    data = bytearray(args.object.read_bytes())
    if data[:6] != b"\x7fELF\x01\x02":
        sys.exit(f"{args.object}: expected a big-endian ELF32 object")
    if len(data) < 0x34:
        sys.exit(f"{args.object}: truncated ELF header")
    section_offset = struct.unpack_from(">I", data, 0x20)[0]
    section_size, section_count, names_index = struct.unpack_from(">HHH", data, 0x2e)
    if section_size < 0x28 or names_index >= section_count:
        sys.exit(f"{args.object}: invalid ELF section table")

    def section_header(index: int) -> tuple[int, int, int]:
        offset = section_offset + index * section_size
        if offset + 0x28 > len(data):
            sys.exit(f"{args.object}: truncated ELF section table")
        name_offset = struct.unpack_from(">I", data, offset)[0]
        file_offset, size = struct.unpack_from(">II", data, offset + 0x10)
        return name_offset, file_offset, size

    _, names_offset, names_size = section_header(names_index)
    names = data[names_offset:names_offset + names_size]
    sections: dict[str, tuple[int, int]] = {}
    for index in range(section_count):
        name_offset, file_offset, size = section_header(index)
        if name_offset >= len(names):
            sys.exit(f"{args.object}: invalid ELF section name")
        name_end = names.find(0, name_offset)
        if name_end < 0:
            sys.exit(f"{args.object}: unterminated ELF section name")
        name = bytes(names[name_offset:name_end]).decode("ascii", errors="strict")
        sections[name] = (file_offset, size)

    for specification in args.section:
        try:
            name, actual_path, expected_path = specification.split("|", 2)
        except ValueError:
            sys.exit(f"invalid --section value: {specification}")
        if name not in sections:
            sys.exit(f"{args.object}: missing section {name}")
        file_offset, size = sections[name]
        actual = Path(actual_path).read_bytes()
        expected = Path(expected_path).read_bytes()
        if len(actual) != size or len(expected) != size:
            sys.exit(f"{name}: expected {size} bytes, got {len(actual)} and {len(expected)}")
        if file_offset + size > len(data):
            sys.exit(f"{args.object}: truncated section {name}")
        raw = data[file_offset:file_offset + size]
        data[file_offset:file_offset + size] = bytes(
            expected_byte if actual_byte != expected_byte else raw_byte
            for raw_byte, actual_byte, expected_byte in zip(raw, actual, expected)
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Configure and report progress for the SM3DW matching decompilation."
    )
    parser.add_argument("mode",
                        choices=("configure", "progress", "verify", "extract", "make-base"),
                        nargs="?", default="configure")
    parser.add_argument("-v", "--version", choices=VERSIONS, type=str.upper,
                        default=DEFAULT_VERSION, help="game version to build (default: US)")
    parser.add_argument("--build-dir", type=Path, default=Path("build"),
                        help="base build directory (default: build)")
    parser.add_argument("--rpx", type=Path,
                        help="install a legally obtained RedCarpet.rpx into orig/<version>")
    parser.add_argument("--compiler", type=Path, help="path to cxppc.exe")
    parser.add_argument("--binutils", type=Path,
                        help="directory containing powerpc-eabi binutils")
    parser.add_argument("--wrapper", type=Path,
                        help="path to wibo or Wine (wibo is downloaded by default)")
    parser.add_argument("--wiiurpxtool", type=Path,
                        help="path to an existing wiiurpxtool executable")
    parser.add_argument("--non-matching", action="store_true",
                        help="keep building and generate objdiff bases for mismatching code")
    parser.add_argument("--no-progress", dest="progress", action="store_false",
                        help="do not make verification progress part of the default target")
    parser.add_argument("--verbose", action="store_true",
                        help="print per-file progress details")
    parser.add_argument("--actual", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--stamp", type=Path)
    parser.add_argument("--object", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--script", type=Path)
    parser.add_argument("--section-start", type=lambda value: int(value, 0))
    parser.add_argument("--section-end", type=lambda value: int(value, 0))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--address", type=lambda value: int(value, 0))
    parser.add_argument("--size", type=lambda value: int(value, 0))
    parser.add_argument("--section", action="append")
    args = parser.parse_args()
    if args.mode == "configure":
        configure(args)
    elif args.mode == "progress":
        progress(args)
    elif args.mode == "verify":
        verify(args)
    elif args.mode == "extract":
        extract(args)
    else:
        make_base(args)


if __name__ == "__main__":
    main()
