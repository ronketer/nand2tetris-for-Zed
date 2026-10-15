# Nand2Tetris for Zed

A declarative Zed extension for the languages used in Nand2Tetris: HDL (`.hdl`), Hack assembly (`.asm`) and Jack (`.jack`). It adds language configuration and Tree-sitter queries using community parsers.

## Current scope

- File associations, comment configuration and syntax highlighting for the three languages.
- Outline and indentation queries for HDL and Jack.
- HDL chip snippets registered by `extension.toml`.
- Small example files for manual development checks.

`snippets/jack.json` is present in the repository but is not registered in the current manifest, so Jack snippets are not advertised as an enabled feature. There is no language server, compiler, simulator or semantic diagnostics implementation. Tree-sitter highlighting does not establish semantic correctness.

## Installation status

The [Zed registry submission](https://github.com/zed-industries/extensions/pull/6508) is open and unmerged as of October 15, 2026. Use a development installation; registry availability and download counts are not claimed.

```bash
git clone https://github.com/ronketer/nand2tetris-for-Zed.git
```

In Zed, open the command palette, choose `extensions: install dev extension`, and select the repository root. Parser acquisition requires access to the grammar repositories. This extension contains no custom Rust implementation, but its Tree-sitter grammars still need to be acquired and loaded by Zed.

## Implementation and attribution

The project integrates language settings, highlight/outline/indent queries and snippets. It does not implement the parsers below.

| Language | Community grammar | Pinned revision |
| --- | --- | --- |
| HDL | [quantonganh/tree-sitter-hdl](https://github.com/quantonganh/tree-sitter-hdl) | `2199fdf1d302100a53002ea2cf540999119836a0` |
| Hack assembly | [soconnor0919/tree-sitter-hack-assembly](https://github.com/soconnor0919/tree-sitter-hack-assembly) | `a2442f53ea27dc112b6774cb79504a0787a21919` |
| Jack | [nverno/tree-sitter-jack](https://github.com/nverno/tree-sitter-jack) | `1a617413ea92c237bff4cbe7fa67eb3bf4425596` |

The authoritative configuration is [extension.toml](extension.toml). Grammar projects retain their own authorship and licenses. Nand2Tetris is the associated educational curriculum, not a parser or course authored by this extension project.

## Manual validation

No automated validation suite is committed. After installing the development extension:

1. Open each file under `examples/` and confirm its language association and highlighting.
2. In HDL and Jack, inspect indentation and the symbol outline.
3. Try the configured comment shortcut for all three languages.
4. In HDL, expand a chip snippet and inspect parameter placeholders and the terminator.
5. Check Zed's logs for grammar/query errors and record the Zed version and platform with any bug report.

These are suggested smoke checks, not a claim that they passed during this audit. Use original non-solution fixtures for future tests rather than publishing additional course answers.

## License

Extension code is MIT-licensed; see [LICENSE](LICENSE). Third-party grammar and educational-material terms remain separate.
