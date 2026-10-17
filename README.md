# Nand2Tetris for Zed

A declarative Zed extension for the languages used in Nand2Tetris: HDL (`.hdl`), Hack assembly (`.asm`) and Jack (`.jack`). It adds language configuration and Tree-sitter queries using community parsers.

## Current scope

- File associations, comment configuration and syntax highlighting for the three languages.
- Outline and indentation queries for HDL and Jack.
- HDL chip snippets and Jack boilerplate snippets registered by `extension.toml`.
- Small example files for manual development checks.

There is no language server, compiler, simulator or semantic diagnostics implementation. Tree-sitter highlighting does not establish semantic correctness.

## Development installation

Follow the [Zed registry submission](https://github.com/zed-industries/extensions/pull/6508) for publication status. To test this repository directly:

```bash
git clone https://github.com/ronketer/nand2tetris-for-Zed.git
```

In Zed, choose `zed: install dev extension` from the command palette (or **Install Dev Extension** from the Extensions page), and select the repository root.

Zed needs network access to the grammar repositories and downloads the `wasi-sdk` to compile their Tree-sitter parsers. To use an existing SDK, set `WASI_SDK_PATH` to its root directory. This extension has no custom Rust implementation. See [Zed's development guide](https://zed.dev/docs/extensions/developing-extensions) for toolchain setup.

For installation or grammar errors, run `zed: open log`. You can also launch Zed from a terminal with `zed --foreground` for more logging.

## Implementation and attribution

The project integrates language settings, highlight/outline/indent queries and snippets. It does not implement the parsers below.

| Language | Community grammar | Pinned revision |
| --- | --- | --- |
| HDL | [quantonganh/tree-sitter-hdl](https://github.com/quantonganh/tree-sitter-hdl) | `2199fdf1d302100a53002ea2cf540999119836a0` |
| Hack assembly | [soconnor0919/tree-sitter-hack-assembly](https://github.com/soconnor0919/tree-sitter-hack-assembly) | `a2442f53ea27dc112b6774cb79504a0787a21919` |
| Jack | [nverno/tree-sitter-jack](https://github.com/nverno/tree-sitter-jack) | `1a617413ea92c237bff4cbe7fa67eb3bf4425596` |

The authoritative configuration is [extension.toml](extension.toml). Grammar projects retain their own authorship and licenses. Nand2Tetris is the associated educational curriculum, not a parser or course authored by this extension project.

## Automated validation

Use Python 3.13, Git, and a GCC/Clang-compatible C compiler on `PATH` (or set `CC`). On Windows, use a 64-bit compiler matching your Python installation; the validator does not use MSVC's `cl` command.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/validate.py
git diff --check
```

On Linux, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`. The validator fetches the exact grammar revisions from `extension.toml` and builds native libraries in the OS temporary directory. It checks all query files, expected highlights and outline symbols, the examples, snippet expansions (including populated Jack return values), indentation ranges, and resource registration. These are syntax checks, not compilation or semantic checks. On Windows, loaded DLLs can remain in the temporary directory until cleaned up by the OS.

GitHub Actions runs the validator and a Linux x86_64 packaging check with the same pinned `zed-extension` CLI revision used by the registry. To run that packaging check yourself on Linux or in Ubuntu WSL:

```bash
bash scripts/package.sh
```

The packaging command downloads the CLI and build dependencies, reports its temporary output directory, and does not publish the package.

### Known HDL parser limitations

The pinned upstream HDL parser currently rejects these syntax forms:

- Ordinary `/* ... */` comments (including the block-comment delimiter configured for HDL).
- Indexed part pins such as `SamplePart(in[0]=a, out[0]=out);`.
- Bus-range connections such as `SamplePart(in=bus[0..7], out=out);`.

These three cases appear as **expected failures** in validation, tied to the current HDL revision. An unexpected pass fails the suite so the expectation can be reviewed. Changing the grammar pin or providing `--hdl-source` requires all three cases to pass normally. Native parser validation does not establish that the same behavior has been checked inside Zed.

To test a proposed upstream fix without changing the manifest, use Tree-sitter CLI 0.25.8 in a temporary copy of the grammar checkout. Run `tree-sitter generate --abi 14` and `tree-sitter test` there, then pass that copy to the validator:

```powershell
.\.venv\Scripts\python.exe scripts/validate.py --hdl-source C:\path\to\generated-grammar
```

The supplied directory must contain the generated `src/parser.c` and its headers. Keep grammar fixes separate from the extension and only update the manifest pin after an upstream fix is accepted and publicly available.

## Manual validation in Zed

After installing the development extension at the exact commit proposed for the registry:

1. Open each file under `examples/` and confirm its language association and highlighting.
2. In HDL and Jack, inspect indentation and the symbol outline.
3. Try the configured comment shortcut for all three languages.
4. In HDL and Jack, expand a snippet and inspect parameter placeholders and the terminator.
5. Run `zed: open log`, check for grammar/query errors, and record the source commit, Zed version, platform, and results.

Manual Zed testing is a [publishing prerequisite](https://zed.dev/docs/extensions/publishing/prerequisites). Automated validation and successful packaging do not replace it. Test fixtures should be small, original syntax examples rather than additional course solutions.

## License

Extension code is MIT-licensed; see [LICENSE](LICENSE). Third-party grammar and educational-material terms remain separate.
