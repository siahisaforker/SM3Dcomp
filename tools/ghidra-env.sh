#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export JAVA_HOME="$repo_root/.local/jdk-21"
export GHIDRA_HOME="$repo_root/.local/ghidra"
export XDG_CACHE_HOME="$repo_root/.local/xdg/cache"
export XDG_CONFIG_HOME="$repo_root/.local/xdg/config"
export XDG_DATA_HOME="$repo_root/.local/xdg/share"
export PATH="$JAVA_HOME/bin:$PATH"

if [[ ! -x "$JAVA_HOME/bin/java" || ! -x "$GHIDRA_HOME/ghidraRun" ]]; then
    printf 'Ghidra is not installed; run python3 configure.py ghidra first.\n' >&2
    return 1 2>/dev/null || exit 1
fi

mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
