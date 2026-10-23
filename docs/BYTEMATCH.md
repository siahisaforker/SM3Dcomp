# ByteMatch progress

ByteMatch ingests objdiff v2 reports uploaded by successful GitHub Actions runs on the default branch. SM3Dcomp's locally generated `build/US/report.json` is **not** an objdiff v2 report. The ByteMatch adapter writes a separate `build/US/bytematch/report.json`.

## Initial setup

1. Sign in at <https://bytematch.dev> with the GitHub account that administers `siahisaforker/SM3Dcomp`.
2. Under **Manage → Add project**, register `siahisaforker/SM3Dcomp`.
3. ByteMatch will ingest successful `main` push runs whose artifact is named `US_report`. This is produced by `.github/workflows/bytematch.yml`. No upload token is needed. If ingestion cannot access artifacts, install the ByteMatch GitHub App from the project's manage page.
4. The intended page is <https://bytematch.dev/siahisaforker/SM3Dcomp> after registration and ingestion.

## Updating progress

The proprietary RPX and GHS toolchain cannot run on public GitHub Actions. Instead, verify locally and commit an evidence-derived snapshot **only after strict binary matching**:

```sh
python3 configure.py
ninja -j2 progress
python3 tools/bytematch_report.py update
python3 -m unittest discover -s tests -q
```

`update` runs split validation, checks the original RPX SHA-256, compares the local report to fresh strict verification stamps, and writes `config/US/bytematch_snapshot.json`. The snapshot contains **function names, addresses, sizes, and hashes of match-affecting inputs**, not proprietary game bytes.

GitHub Actions runs `generate` and rejects the snapshot if any source, header, split, symbol, configuration, or build-generator input has changed since verification. If it fails, rerun the steps above on a local machine with the original RPX/toolchain and commit the regenerated snapshot along with the code. `generate` does not claim new matches just because a source file exists.

To inspect the generated report without the RPX:

```sh
python3 tools/bytematch_report.py generate
python3 tools/bytematch_report.py check
```

## Progress semantics

- `total_code` is the original US RPX's 7,335,668-byte `.text` region.
- `matched_code` is the sum of function sizes from the verified snapshot, whose matches must agree with strict local build verification.
- `total_functions` currently uses **30,941 provisional Ghidra function entries**, including functions with noncontiguous bodies. This is an *estimate*, not a verified function total or original object split count; the function badge should be interpreted accordingly.
- Currently verified source files are displayed as their own units; all code not assigned to a known split appears under **Unmapped .text (not an original object split)**. The unmapped unit is for coverage accounting only, **not** a recovered original translation unit.
- ByteMatch currently tracks code only. No matched data is claimed.

Documentation: <https://bytematch.dev/docs/getting-started>
