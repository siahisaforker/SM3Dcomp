#!/usr/bin/env python3

# it's in the name

import argparse
import hashlib
import os
import platform
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

from download_tool import download


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def obtain(url: str, expected: str, archive: Path) -> None:
    if archive.is_file() and sha256(archive) == expected:
        print(f"Using {archive}")
        return
    archive.unlink(missing_ok=True)
    print(f"Downloading {url}")
    download(url, archive, executable=False)
    actual = sha256(archive)
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


def validate(java_home: Path, ghidra: Path) -> None:
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


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Install Ghidra, GhidraRPXLoader, and Java 21 under .local."
    )
    parser.add_argument(
        "--prefix", type=Path, default=root / ".local",
        help="installation prefix (default: repository .local)"
    )
    args = parser.parse_args()
    prefix = args.prefix.resolve()
    downloads = prefix / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    machine = platform.machine().lower()
    if platform.system() != "Linux" or machine not in ("x86_64", "amd64"):
        raise SystemExit(
            "automatic Java installation currently supports Linux x86_64; "
            "install a Java 21 JDK manually and update tools/ghidra-env.sh"
        )

    java_archive = downloads / TEMURIN_ARCHIVE
    ghidra_archive = downloads / GHIDRA_ARCHIVE
    extension_archive = downloads / GHIDRARPX_ARCHIVE
    obtain(TEMURIN_URL, TEMURIN_SHA256, java_archive)
    obtain(GHIDRA_URL, GHIDRA_SHA256, ghidra_archive)
    obtain(GHIDRARPX_URL, GHIDRARPX_SHA256, extension_archive)

    java_home = prefix / "jdk-21"
    ghidra = prefix / "ghidra"
    install_archive(
        java_archive, java_home, TEMURIN_VERSION, extract_tar, ".sm3dcomp-version"
    )
    install_archive(
        ghidra_archive, ghidra, GHIDRA_VERSION, extract_zip, ".sm3dcomp-version"
    )
    install_extension(extension_archive, ghidra)
    ensure_launch_permissions(ghidra)
    validate(java_home, ghidra)


if __name__ == "__main__":
    main()
