# Nand2Tetris for Zed

A lightweight, pure-declarative language extension for the **Zed** editor that adds support and syntax highlighting for all three languages featured in the **Nand2Tetris** (The Elements of Computing Systems) curriculum:

- **HDL (`.hdl`)**: Hardware Description Language used for gate-level hardware designs.
- **Hack Assembly (`.asm`)**: Low-level symbolic assembly for the Hack CPU.
- **Jack (`.jack`)**: High-level, Java-like object-oriented programming language.

Since this extension is purely declarative, it does not contain any Rust compilation overhead, making it load instantly in the Zed editor.

---

## Features

- **Tree-sitter Syntax Highlighting**: Accurate, semantic syntax highlighting using community-maintained Tree-sitter parsers.
- **Intelligent Autocompletion (Snippets)**: Quick and accurate autocomplete suggestions for all 37 core Hack chips. Each suggestion displays the parameter signature (inputs and outputs) in the completion dropdown and expands into a tab-traversable template (automatically ending with a semicolon).
- **Auto-Comments Toggle**: Toggle line comments using your standard editor keybindings (`Ctrl-/` or `Cmd-/`).
- **File Suffix Association**: Automatically detects and applies syntax rules to `.hdl`, `.asm`, and `.jack` files.

---

## Directory Structure

```text
nand2tetris-for-Zed/
├── extension.toml          # Extension manifest (defines repositories, revisions, and snippets)
├── snippets/
│   └── hdl.json            # Autocomplete snippets with parameter signatures for the Hack chip set
├── languages/
│   ├── hack-assembly/
│   │   ├── config.toml     # File suffix mapping and comment symbols for Hack ASM
│   │   └── highlights.scm  # Highlight query for instructions, registers, and labels
│   ├── hdl/
│   │   ├── config.toml     # File suffix mapping and comment symbols for HDL
│   │   └── highlights.scm  # Highlight query for chips, inputs, outputs, and connections
│   └── jack/
│       ├── config.toml     # File suffix mapping and comment symbols for Jack
│       └── highlights.scm  # Highlight query for classes, methods, parameters, and expressions
├── tests/
│   ├── test.hdl            # Sample XOR gate to test HDL highlighting
│   ├── test.asm            # Sample multiplication loop to test Hack Assembly highlighting
│   └── test.jack           # Sample class to test Jack highlighting
└── README.md
```

---

## Tree-sitter Grammars Used

The extension registers the following open-source Tree-sitter grammars:

| Language | Repository | Target Grammar Name |
| :--- | :--- | :--- |
| **HDL** | [quantonganh/tree-sitter-hdl](https://github.com/quantonganh/tree-sitter-hdl) | `hdl` |
| **Hack Assembly** | [soconnor0919/tree-sitter-hack-assembly](https://github.com/soconnor0919/tree-sitter-hack-assembly) | `hack_assembly` |
| **Jack** | [nverno/tree-sitter-jack](https://github.com/nverno/tree-sitter-jack) | `jack` |

---

## How to Install (Local Development)

To run and test this extension locally in Zed:

1. Clone this repository to your local system:
   ```bash
   git clone https://github.com/ronketer/nand2tetris-for-Zed.git
   ```
2. Open **Zed**.
3. Open the Command Palette (`Ctrl-Shift-P` on Windows/Linux or `Cmd-Shift-P` on macOS).
4. Select `extensions: install dev extension`.
5. Choose the root folder of this project (`nand2tetris-for-ZED`).
6. Zed will instantly load the extension, download the registered Tree-sitter parsers, and apply syntax highlighting to any open `.hdl`, `.asm`, or `.jack` files.
