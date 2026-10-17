#!/usr/bin/env bash
# Linux x86_64 packaging smoke check; does not publish anything.
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
work_dir="$(mktemp -d "${RUNNER_TEMP:-${TMPDIR:-/tmp}}/nand2tetris-package.XXXXXX")"
# Match the revision used by zed-industries/extensions CI.
cli_sha=9ee3c503a4bbbc6b4a0f8a789acca4871d773223
cli="$work_dir/zed-extension"
echo "Packaging artifacts: $work_dir"

curl --fail --location --retry 3 \
  "https://zed-extension-cli.nyc3.digitaloceanspaces.com/$cli_sha/x86_64-unknown-linux-gnu/zed-extension" \
  --output "$cli"
chmod +x "$cli"
RUST_LOG=info "$cli" --source-dir "$source_dir" \
  --scratch-dir "$work_dir/scratch" \
  --output-dir "$work_dir/output"
test -s "$work_dir/output/manifest.json"
echo "Packaged extension: $work_dir/output"
