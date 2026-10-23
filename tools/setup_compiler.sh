#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DESTINATION="${1:-"$SCRIPT_DIR/../.local/toolchains/ghs5.3.22"}"

ARCHIVE_NAME="ghs5.3.22.tar.gz"
DOWNLOAD_URL="https://github.com/decompme/compilers/releases/download/compilers/$ARCHIVE_NAME"
EXPECTED_SHA256="41CD0A4723ACFBDDF8F70A9C3FF84BCE7E85087B1D1CCEF8BBF5F03D82C2B520"

DOWNLOAD_DIR="$SCRIPT_DIR/../.local/downloads"
ARCHIVE_PATH="$DOWNLOAD_DIR/$ARCHIVE_NAME"

mkdir -p "$DOWNLOAD_DIR" "$DESTINATION"

if [[ ! -f "$ARCHIVE_PATH" ]]; then
    echo "Downloading $ARCHIVE_NAME..."

    if command -v curl >/dev/null 2>&1; then
        curl --fail --location \
            --output "$ARCHIVE_PATH" \
            "$DOWNLOAD_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget --output-document="$ARCHIVE_PATH" "$DOWNLOAD_URL"
    else
        echo "error: curl or wget is required to download the compiler" >&2
        exit 1
    fi
fi

if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_SHA256="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL_SHA256="$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')"
else
    echo "error: sha256sum or shasum is required" >&2
    exit 1
fi

if [[ "${ACTUAL_SHA256^^}" != "$EXPECTED_SHA256" ]]; then
    echo "error: GHS archive digest mismatch" >&2
    echo "expected: $EXPECTED_SHA256" >&2
    echo "actual:   ${ACTUAL_SHA256^^}" >&2
    exit 1
fi

tar -xzf "$ARCHIVE_PATH" -C "$DESTINATION"

COMPILER="$DESTINATION/bin/cxppc.exe"

if [[ ! -f "$COMPILER" ]]; then
    echo "error: compiler was not found after extraction: $COMPILER" >&2
    exit 1
fi

echo "Installed GHS 5.3.22: $DESTINATION"
