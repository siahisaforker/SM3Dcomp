#!/usr/bin/env python3

# downloads tools

import argparse
import os
import platform
import shutil
import stat
import ssl
import urllib.error
import urllib.request
from pathlib import Path


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=("wibo",))
    parser.add_argument("output", type=Path)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    url = wibo_url(args.tag)
    print(f"Downloading {url}")
    download(url, args.output)


if __name__ == "__main__":
    main()
