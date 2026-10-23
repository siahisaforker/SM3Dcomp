#!/usr/bin/env python3

"""Configure and build the Wii U matching decompilation."""

import argparse
import urllib.request
import urllib.error
import zipfile
import tempfile
import tarfile
import subprocess
import stat
import ssl
import platform
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
    text_address: int
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
        text_address=config_int(values, path, "text_address"),
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


def load_import_maps(root: Path, paths: tuple[Path, ...]) -> dict[str, int]:
    """Import addresses are local RPX-derived data, absent on clean checkouts."""
    available = tuple(path for path in paths if (root / path).is_file())
    if not available:
        return {}
    if len(available) != len(paths):
        missing = [str(path) for path in paths if not (root / path).is_file()]
        sys.exit("incomplete local import maps: " + ", ".join(missing) +
                 "\nrun python3 configure.py imports with the original RPX locally")
    return load_undefined_maps(root, available)


def load_linker_symbols(root: Path, project: ProjectConfig) -> dict[str, int]:
    values = load_undefined_maps(root, project.undefined_maps)
    for name, address in load_import_maps(root, project.import_maps).items():
        if name in values and values[name] != address:
            sys.exit(f"conflicting address for {name} between undefined and import maps")
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
    undefined = load_linker_symbols(root, project)
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
    download_tool = root / "configure.py"
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
        "  command = $python configure.py download-tool --tool $tool --output $out --tag $tag",
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
        "configure.py",
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
    undefined = load_linker_symbols(root, project)
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


PROJECT_ROOT = Path(__file__).resolve().parent

@dataclass(frozen=True)
class ImportSection:
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


def import_error(message):
    raise ValueError(message)


def get_string(data, offset):
    if offset < 0 or offset >= len(data):
        import_error("invalid string table offset")
    end = data.find(b"\0", offset)
    if end < 0:
        import_error("unterminated ELF string")
    return data[offset:end].decode("utf-8")


def read_imports(data):
    if len(data) < 52 or data[:7] != b"\x7fELF\x01\x02\x01":
        import_error("expected a big-endian ELF32 file")
    elf_type, machine = struct.unpack_from(">HH", data, 16)
    if elf_type != 0xFE01 or machine != 20:
        import_error("expected a Wii U PowerPC RPX ELF")
    shoff = struct.unpack_from(">I", data, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from(">HHH", data, 46)
    if shentsize != 40 or shnum == 0 or shstrndx >= shnum:
        import_error("invalid ELF section headers")
    if shoff + shnum * shentsize > len(data):
        import_error("ELF section headers outside file")
    raw = [struct.unpack_from(">IIIIIIIIII", data, shoff + index * shentsize)
           for index in range(shnum)]

    def section_data(header):
        _, kind, _, _, offset, size, _, _, _, _ = header
        if kind == 8 or offset + size > len(data):
            import_error("ELF section data outside file")
        return data[offset:offset + size]

    section_names = section_data(raw[shstrndx])
    sections = [ImportSection(get_string(section_names, header[0]), header[1], header[4],
                        header[5], header[6], header[9]) for header in raw]
    imports = []
    seen = {}
    for section_index, section in enumerate(sections):
        if section.kind != 2:  # SHT_SYMTAB
            continue
        if section.entsize != 16 or section.size % section.entsize or section.link >= shnum:
            import_error("invalid ELF symbol table")
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
                import_error("invalid imported symbol name")
            if name in seen and seen[name] != (address, section_name):
                import_error(f"conflicting imported symbol {name}")
            seen[name] = (address, section_name)
            imports.append(Import(section_name, name, address, "function" if kind == 2 else "data"))
    if not imports:
        import_error("no imported symbols found")
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


def generate_import_maps(elf, output, check):
    expected = import_files(read_imports(elf.read_bytes()))
    existing = {path.name for path in output.glob("*.txt")}
    if check:
        problems = [name for name, text in expected.items()
                    if not (output / name).is_file() or (output / name).read_text() != text]
        problems += sorted(existing - expected.keys())
        if problems:
            import_error("stale import maps: " + ", ".join(sorted(problems)))
    else:
        output.mkdir(parents=True, exist_ok=True)
        for name, text in expected.items():
            path = output / name
            if not path.is_file() or path.read_text() != text:
                path.write_text(text)
    print(f"{sum(len(text.splitlines()) - 3 for text in expected.values())} imported symbols "
          f"in {len(expected)} maps ({'verified' if check else 'generated'})")
    return sorted(expected)



SYMBOL_RE = re.compile(
    r"^([^=\s]+)\s*=\s*(\.[\w.$]+):(0x[0-9a-fA-F]+|\d+)\s*;\s*(?://\s*size:\s*(0x[0-9a-fA-F]+|\d+))?\s*$"
)
SPLIT_RE = re.compile(
    r"^\s+(\.[\w.$]+)\s+start:(0x[0-9a-fA-F]+|\d+)\s+end:(0x[0-9a-fA-F]+|\d+)\s*$"
)


def validation_error(message):
    raise ValueError(message)


def read_validated_symbols(path):
    result = []
    seen_names = set()
    seen_addresses = set()
    for line_number, original in enumerate(path.read_text().splitlines(), 1):
        line = original.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        match = SYMBOL_RE.fullmatch(line)
        if not match:
            validation_error(f"{path}:{line_number}: malformed symbol")
        name, section, raw_address, raw_size = match.groups()
        if not raw_size:
            validation_error(f"{path}:{line_number}: function size is required")
        address, size = int(raw_address, 0), int(raw_size, 0)
        if name in seen_names or (section, address) in seen_addresses:
            validation_error(f"{path}:{line_number}: duplicate name or address")
        if section == ".text" and (address % 4 or size % 4):
            validation_error(f"{path}:{line_number}: PowerPC instructions must be 4-byte aligned")
        if size <= 0:
            validation_error(f"{path}:{line_number}: non-positive function size")
        seen_names.add(name)
        seen_addresses.add((section, address))
        result.append((name, section, address, address + size))
    return result


def read_validated_splits(path, text_start, text_end):
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
                validation_error(f"{path}:{line_number}: duplicate or unsafe source path")
            seen_sources.add(current_source)
            if not (PROJECT_ROOT / "src" / current_source).is_file():
                validation_error(f"{path}:{line_number}: missing source: {current_source}")
            continue
        match = SPLIT_RE.fullmatch(original)
        if current_source is None or not match:
            validation_error(f"{path}:{line_number}: malformed split")
        section, raw_start, raw_end = match.groups()
        start, end = int(raw_start, 0), int(raw_end, 0)
        if start >= end:
            validation_error(f"{path}:{line_number}: empty or reversed range")
        if section == ".text":
            if start < text_start or end > text_end or start % 4 or end % 4:
                validation_error(f"{path}:{line_number}: out-of-bounds or unaligned .text")
        result.append((current_source, section, start, end))
    if not result:
        validation_error(f"{path}: no source units")
    for section in {item[1] for item in result}:
        ranges = sorted((start, end, source) for source, sec, start, end in result if sec == section)
        for (_, earlier_end, earlier_source), (start, _, source) in zip(ranges, ranges[1:]):
            if start < earlier_end:
                validation_error(f"overlap in {section}: {earlier_source} / {source} at 0x{start:08x}")
    return result


def validate_manifests():
    project = load_project(PROJECT_ROOT, "US")
    active = read_validated_symbols(PROJECT_ROOT / "config" / "US" / "symbols.txt")
    verified = read_validated_symbols(PROJECT_ROOT / "config" / "US" / "verified_symbols.txt")
    splits = read_validated_splits(PROJECT_ROOT / "config" / "US" / "splits.txt",
                                    project.text_address, project.text_address + project.text_size)
    verification = {(section, start, end) for _, section, start, end in verified}
    active_ranges = sorted((start, end) for _, section, start, end in active if section == ".text")
    for (_, prev_end), (start, _) in zip(active_ranges, active_ranges[1:]):
        if start < prev_end:
            validation_error(f"active symbol overlap at 0x{start:08x}")
    for name, section, start, end in active:
        covering = [s for s in splits if s[1] == section and s[2] <= start and end <= s[3]]
        if len(covering) != 1:
            validation_error(f"{name}: must be contained in exactly one matching split")
        if (section, start, end) not in verification:
            validation_error(f"{name}: no identically bounded verified PowerPC function")
    for source, section, start, end in splits:
        if not any(sym_section == section and sym_start >= start and sym_end <= end
                   for _, sym_section, sym_start, sym_end in active):
            validation_error(f"{source}: no named function in split 0x{start:08x}-0x{end:08x}")
    rp = PROJECT_ROOT / "orig" / "US" / "RedCarpet.rpx"
    if rp.is_file():
        actual = hashlib.sha256(rp.read_bytes()).hexdigest()
        if actual != project.sha256:
            validation_error(f"original executable SHA-256 differs: {actual}")
    covered = sum(end - start for _, section, start, end in splits if section == ".text")
    rp_status = "RPX fingerprint verified" if rp.is_file() else "RPX not present"
    print(f"valid: {len(splits)} split ranges, {len(active)} matching targets, "
          f"{len(verified)} verified research symbols, {covered} bytes of active text; "
          f"{rp_status}")



def wibo_url(tag: str) -> str:
    machine = platform.machine().lower()
    if machine == "amd64":
        machine = "x86_64"
    if platform.system().lower() == "darwin":
        machine = "macos"
    return f"https://github.com/decompals/wibo/releases/download/{tag}/wibo-{machine}"


def download(url: str, output: Path, executable: bool = True) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "SM3Dcomp"})
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as error:
        if "CERTIFICATE_VERIFY_FAILED" not in str(error):
            raise
        try:
            import certifi
        except ImportError:
            raise SystemExit(
                "TLS verification failed; install certifi with "
                "`python3 -m pip install certifi`"
            ) from error
        response = urllib.request.urlopen(
            request, context=ssl.create_default_context(cafile=certifi.where())
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        with response, temporary.open("wb") as stream:
            shutil.copyfileobj(response, stream)
        if executable:
            mode = os.stat(temporary).st_mode
            os.chmod(temporary, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)



GHIDRA_VERSION = "12.1.2"
GHIDRA_ARCHIVE = "ghidra_12.1.2_PUBLIC_20260605.zip"
GHIDRA_URL = (
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/"
    f"Ghidra_12.1.2_build/{GHIDRA_ARCHIVE}"
)
GHIDRA_SHA256 = "b62e81a0390618466c019c60d8c2f796ced2509c4c1aea4a37644a77272cf99d"

GHIDRARPX_VERSION = "0.9.2"
GHIDRARPX_ARCHIVE = "GhidraRPXLoader-0.9.2-d496d43-Ghidra_12.0.zip"
GHIDRARPX_URL = (
    "https://github.com/Maschell/GhidraRPXLoader/releases/download/"
    f"v0.9.2/{GHIDRARPX_ARCHIVE}"
)
GHIDRARPX_SHA256 = "b010bcc771f224421c8fa370c0023eca1a46c94cf0a71b51982d5b601c501b8b"

TEMURIN_VERSION = "21.0.12+8"
TEMURIN_ARCHIVE = "OpenJDK21U-jdk_x64_linux_hotspot_21.0.12_8.tar.gz"
TEMURIN_URL = (
    "https://github.com/adoptium/temurin21-binaries/releases/download/"
    f"jdk-21.0.12%2B8/{TEMURIN_ARCHIVE}"
)
TEMURIN_SHA256 = "e4446ff06a276155697597cc0f1b15da004ff083f4964a35271ecee567177370"



def obtain(url: str, expected: str, archive: Path) -> None:
    if archive.is_file() and file_sha256(archive) == expected:
        print(f"Using {archive}")
        return
    archive.unlink(missing_ok=True)
    print(f"Downloading {url}")
    download(url, archive, executable=False)
    actual = file_sha256(archive)
    if actual != expected:
        archive.unlink(missing_ok=True)
        raise SystemExit(
            f"{archive}: SHA-256 mismatch\nexpected {expected}\nactual   {actual}"
        )


def checked_members(names: list[str], archive: Path) -> None:
    for name in names:
        member = Path(name)
        if member.is_absolute() or ".." in member.parts:
            raise SystemExit(f"{archive}: unsafe archive member {name}")


def extract_zip(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as source:
        checked_members(source.namelist(), archive)
        source.extractall(destination)


def extract_tar(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as source:
        checked_members([member.name for member in source.getmembers()], archive)
        if sys.version_info >= (3, 12):
            source.extractall(destination, filter="fully_trusted")
        else:
            source.extractall(destination)


def only_directory(path: Path, archive: Path) -> Path:
    entries = list(path.iterdir())
    if len(entries) != 1 or not entries[0].is_dir():
        raise SystemExit(f"{archive}: expected one top-level directory")
    return entries[0]


def install_archive(
    archive: Path,
    destination: Path,
    version: str,
    extractor,
    marker_name: str,
) -> None:
    marker = destination / marker_name
    if marker.is_file() and marker.read_text(encoding="utf-8").strip() == version:
        print(f"Using {destination}")
        return
    if destination.exists():
        raise SystemExit(
            f"{destination} already exists but is not the pinned {version} install; "
            "move it aside and rerun"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{destination.name}-", dir=destination.parent
    ) as temporary_name:
        temporary = Path(temporary_name)
        extractor(archive, temporary)
        extracted = only_directory(temporary, archive)
        extracted.rename(destination)
    marker.write_text(version + "\n", encoding="utf-8")
    print(f"Installed {destination}")


def install_extension(archive: Path, ghidra: Path) -> None:
    extension_root = ghidra / "Ghidra" / "Extensions"
    destination = extension_root / "GhidraRPXLoader"
    marker = destination / ".sm3dcomp-version"
    if marker.is_file() and marker.read_text(
        encoding="utf-8"
    ).strip() == GHIDRARPX_VERSION:
        print(f"Using {destination}")
        return
    if destination.exists():
        raise SystemExit(
            f"{destination} already exists but is not GhidraRPXLoader "
            f"{GHIDRARPX_VERSION}; move it aside and rerun"
        )
    extension_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".GhidraRPXLoader-", dir=extension_root
    ) as temporary_name:
        temporary = Path(temporary_name)
        extract_zip(archive, temporary)
        extracted = only_directory(temporary, archive)
        extracted.rename(destination)
    marker.write_text(GHIDRARPX_VERSION + "\n", encoding="utf-8")
    print(f"Installed {destination}")


def ensure_launch_permissions(ghidra: Path) -> None:
    for path in (
        ghidra / "ghidraRun",
        ghidra / "support" / "analyzeHeadless",
        ghidra / "support" / "launch.sh",
    ):
        mode = os.stat(path).st_mode
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def validate_ghidra(java_home: Path, ghidra: Path) -> None:
    java = java_home / "bin" / ("java.exe" if platform.system() == "Windows" else "java")
    headless = ghidra / "support" / (
        "analyzeHeadless.bat" if platform.system() == "Windows" else "analyzeHeadless"
    )
    extension = (
        ghidra / "Ghidra" / "Extensions" / "GhidraRPXLoader" /
        "lib" / "GhidraRPXLoader.jar"
    )
    for required in (java, headless, extension):
        if not required.is_file():
            raise SystemExit(f"setup is incomplete: missing {required}")
    result = subprocess.run(
        [str(java), "-version"], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=True
    )
    first_line = result.stdout.splitlines()[0] if result.stdout else "Java 21"
    print(first_line)
    print(f"Ghidra {GHIDRA_VERSION} with GhidraRPXLoader {GHIDRARPX_VERSION} is ready")



GHS_ARCHIVE = "ghs5.3.22.tar.gz"
GHS_URL = "https://github.com/decompme/compilers/releases/download/compilers/" + GHS_ARCHIVE
GHS_SHA256 = "41cd0a4723acfbddf8f70a9c3ff84bce7e85087b1d1ccef8bbf5f03d82c2b520"


def setup_compiler(destination: Path) -> None:
    destination = destination.resolve()
    executable = destination / "bin" / "cxppc.exe"
    if executable.is_file():
        print(f"Using {destination}")
        return
    if destination.exists():
        raise SystemExit(f"incomplete compiler installation at {destination}; move it aside")
    archive = PROJECT_ROOT / ".local" / "downloads" / GHS_ARCHIVE
    obtain(GHS_URL, GHS_SHA256, archive)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".ghs-") as name:
        stage = Path(name) / "ghs"
        stage.mkdir()
        extract_tar(archive, stage)
        if not (stage / "bin" / "cxppc.exe").is_file():
            raise SystemExit(f"missing bin/cxppc.exe in {archive}")
        stage.rename(destination)
    print(f"Installed {destination}")


def setup_ghidra(prefix: Path) -> None:
    prefix = prefix.resolve()
    downloads = prefix / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    machine = platform.machine().lower()
    if platform.system() != "Linux" or machine not in ("x86_64", "amd64"):
        raise SystemExit("automatic Ghidra installation requires Linux x86_64")
    java_archive = downloads / TEMURIN_ARCHIVE
    ghidra_archive = downloads / GHIDRA_ARCHIVE
    extension_archive = downloads / GHIDRARPX_ARCHIVE
    obtain(TEMURIN_URL, TEMURIN_SHA256, java_archive)
    obtain(GHIDRA_URL, GHIDRA_SHA256, ghidra_archive)
    obtain(GHIDRARPX_URL, GHIDRARPX_SHA256, extension_archive)
    java_home = prefix / "jdk-21"
    ghidra = prefix / "ghidra"
    install_archive(java_archive, java_home, TEMURIN_VERSION, extract_tar, ".sm3dcomp-version")
    install_archive(ghidra_archive, ghidra, GHIDRA_VERSION, extract_zip, ".sm3dcomp-version")
    install_extension(extension_archive, ghidra)
    ensure_launch_permissions(ghidra)
    validate_ghidra(java_home, ghidra)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Configure and report progress for the SM3DW matching decompilation."
    )
    parser.add_argument("mode",
                        choices=("configure", "validate", "progress", "verify", "extract", "make-base", "imports", "compiler", "ghidra", "download-tool"),
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
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--elf", type=Path)
    parser.add_argument("--prefix", type=Path, default=PROJECT_ROOT / ".local")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--tool", choices=("wibo",))
    parser.add_argument("--tag", default=WIBO_TAG)
    args = parser.parse_args()
    if args.mode == "validate":
        try:
            validate_manifests()
        except ValueError as error:
            parser.exit(1, f"invalid manifests: {error}\n")
    elif args.mode == "imports":
        try:
            generate_import_maps(args.elf or PROJECT_ROOT / "build" / args.version / "orig" / "RedCarpet.elf",
                                 args.output or PROJECT_ROOT / "config" / args.version / "imports",
                                 args.check)
        except (ValueError, OSError) as error:
            parser.exit(1, f"import extraction: {error}\n")
    elif args.mode == "compiler":
        setup_compiler(args.destination or PROJECT_ROOT / ".local" / "toolchains" / "ghs5.3.22")
    elif args.mode == "ghidra":
        setup_ghidra(args.prefix)
    elif args.mode == "download-tool":
        if args.tool != "wibo" or args.output is None:
            parser.error("download-tool requires --tool wibo and --output")
        download(wibo_url(args.tag), args.output)
    elif args.mode == "configure":
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
