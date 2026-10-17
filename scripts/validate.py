"""Validate the extension using its exact pinned grammar sources.

Requires Git, a GCC/Clang-compatible C compiler, and requirements-dev.txt.
All fetched sources and native libraries are built in an OS temporary directory.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
import warnings

try:
    from tree_sitter import Language, Parser, Query, QueryCursor
except ImportError:
    sys.exit("Install validation dependencies: python -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
HDL_KNOWN_REV = "2199fdf1d302100a53002ea2cf540999119836a0"
HDL_REGRESSIONS = ("block-comment", "indexed-part-pin", "bus-range")


def read_toml(file):
    return tomllib.loads(file.read_text(encoding="utf-8"))


def resource(root, name):
    """Resolve manifest paths inside the extension, including on Windows."""
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f"Missing resource or path outside extension: {name}")
    return target


def validate_layout(root, manifest):
    if manifest.get("schema_version") != 1:
        raise ValueError("Expected schema_version = 1")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest.get("id", "")):
        raise ValueError("Invalid extension ID")
    if not isinstance(manifest.get("version"), str) or not manifest["version"]:
        raise ValueError("Missing extension version")
    for name, grammar in manifest.get("grammars", {}).items():
        if not grammar.get("repository", "").startswith("https://"):
            raise ValueError(f"Grammar {name} must have an HTTPS repository")
        if not re.fullmatch(r"[0-9a-f]{40}", grammar.get("rev", "")):
            raise ValueError(f"Grammar {name} must pin a full commit SHA")
    configs = {}
    suffixes = set()
    for file in sorted((root / "languages").glob("*/config.toml")):
        config = read_toml(file)
        name = config["name"]
        if name in configs or config.get("grammar") not in manifest.get("grammars", {}):
            raise ValueError(f"Duplicate language or unregistered grammar: {name}")
        for suffix in config.get("path_suffixes", []):
            if suffix in suffixes:
                raise ValueError(f"Duplicate language suffix: {suffix}")
            suffixes.add(suffix)
        resource(root, str(file.parent.relative_to(root) / "highlights.scm"))
        configs[name] = (file.parent, config)
    declared = [resource(root, name) for name in manifest.get("snippets", [])]
    bundled = {file.resolve() for file in (root / "snippets").glob("*.json")}
    if set(declared) != bundled or len(declared) != len(set(declared)):
        raise ValueError("Every bundled snippet file must be registered exactly once")
    language_names = {name.lower() for name in configs}
    for file in declared:
        if file.stem not in language_names:
            raise ValueError(f"Snippet filename does not match a language: {file.name}")
        snippets = json.loads(file.read_text(encoding="utf-8"))
        if not snippets:
            raise ValueError(f"Empty snippet file: {file.name}")
        for name, snippet in snippets.items():
            if not snippet.get("prefix") or not snippet.get("description"):
                raise ValueError(f"Missing snippet prefix/description: {name}")
            body = snippet.get("body")
            if not isinstance(body, (str, list)) or not body:
                raise ValueError(f"Missing snippet body: {name}")
    resource(root, "LICENSE")
    return configs


def run(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f"Command failed: {args!r}\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def build_language(name, source, destination):
    compiler = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not compiler:
        raise RuntimeError("Install GCC or Clang, or set CC to a compatible C compiler")
    # A path containing spaces is one executable; CC may also contain flags.
    command = [compiler] if Path(compiler).is_file() else shlex.split(compiler)
    sources = [source / "src/parser.c"]
    scanner = source / "src/scanner.c"
    if scanner.exists():
        sources.append(scanner)
    output = destination / (name + (".dll" if sys.platform == "win32" else ".so"))
    flags = ["-shared", "-O2"]
    if sys.platform != "win32":
        flags.append("-fPIC")
    run(*command, *flags, "-I", str(source / "src"), *map(str, sources), "-o", str(output))
    library = ctypes.CDLL(str(output))
    factory = getattr(library, f"tree_sitter_{name}")
    factory.restype = ctypes.c_void_p
    # tree-sitter 0.25.2 accepts pointers; retain the DLL for the language lifetime.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        language = Language(factory())
    return language, library


def expand_snippet(body, overrides=None):
    """Expand the tab-stop/default forms used by the bundled snippets."""
    text = "\n".join(body) if isinstance(body, list) else body
    values = dict(overrides or {})

    def replace(match):
        braced, default, plain = match.groups()
        index = int(braced or plain)
        if index not in values:
            values[index] = default if default is not None else ("" if braced or index == 0 else f"pin{index}")
        return values[index]

    return re.sub(r"\$\{(\d+)(?::([^}]*))?\}|\$(\d+)", replace, text)


def wrap_snippet(language, name, body):
    if language == "HDL":
        return f"CHIP Sample {{ IN a; OUT out; PARTS: {body} }}"
    if name == "class":
        return body
    if name in {"constructor", "function", "method"}:
        return f"class Sample {{ {body} }}"
    return f"class Sample {{ function void run() {{ {body} }} }}"


class ExtensionTests(unittest.TestCase):
    def parse(self, language, source):
        tree = Parser(self.languages[language]).parse(source.encode("utf-8"))
        self.assertFalse(tree.root_node.has_error, str(tree.root_node))
        return tree

    def captures(self, language, query_name, tree):
        folder, _ = self.configs[language]
        query = Query(self.languages[language], (folder / query_name).read_text(encoding="utf-8"))
        return QueryCursor(query).captures(tree.root_node)

    def test_language_associations(self):
        self.assertEqual({name: config["path_suffixes"] for name, (_, config) in self.configs.items()},
                         {"HDL": ["hdl"], "Hack Assembly": ["asm"], "Jack": ["jack"]})

    def test_examples_and_all_queries(self):
        for name, (folder, config) in self.configs.items():
            source = (ROOT / "examples" / f"test.{config['path_suffixes'][0]}").read_text(encoding="utf-8")
            tree = self.parse(name, source)
            for file in sorted(folder.glob("*.scm")):
                with self.subTest(language=name, query=file.name):
                    captures = self.captures(name, file.name, tree)
                    self.assertTrue(captures, f"No captures for {name}/{file.name}")

    def test_expected_highlights_and_outline_names(self):
        expectations = {
            "HDL": {"type": {"Xor"}, "function": {"Not", "And", "Or"}, "keyword": {"CHIP", "PARTS"}},
            "Hack Assembly": {"label": {"LOOP", "END"}, "keyword": {"JEQ", "JGT", "JMP"}},
            "Jack": {"type": {"Main"}, "function": {"main", "printString", "println"}},
        }
        for name, (_, config) in self.configs.items():
            tree = self.parse(name, (ROOT / "examples" / f"test.{config['path_suffixes'][0]}").read_text(encoding="utf-8"))
            captures = self.captures(name, "highlights.scm", tree)
            for capture, expected in expectations[name].items():
                with self.subTest(language=name, capture=capture):
                    actual = {node.text.decode() for node in captures.get(capture, [])}
                    self.assertTrue(expected <= actual, (expected, actual))
            if name in {"HDL", "Jack"}:
                names = {node.text.decode() for node in self.captures(name, "outline.scm", tree)["name"]}
                self.assertEqual(names, {"Xor"} if name == "HDL" else {"Main", "main"})

    def test_snippet_expansions(self):
        for file in self.manifest["snippets"]:
            language = next(name for name in self.configs if name.lower() == Path(file).stem)
            for name, snippet in json.loads(resource(ROOT, file).read_text(encoding="utf-8")).items():
                with self.subTest(language=language, snippet=name):
                    self.parse(language, wrap_snippet(language, name, expand_snippet(snippet["body"])))

    def test_jack_return_values(self):
        snippets = json.loads((ROOT / "snippets/jack.json").read_text(encoding="utf-8"))
        for kind in ("function", "method"):
            for value in ("", "result"):
                with self.subTest(kind=kind, value=value):
                    expanded = expand_snippet(snippets[kind]["body"], {1: "int" if value else "void", 4: value})
                    tree = self.parse("Jack", wrap_snippet("Jack", kind, expanded))
                    captures = QueryCursor(Query(self.languages["Jack"], "(return_statement) @return")).captures(tree.root_node)
                    self.assertEqual(len(captures.get("return", [])), 1)
                    returned = captures["return"][0].named_children
                    self.assertEqual([node.text.decode() for node in returned], [value] if value else [])

    def test_block_indentation_ranges(self):
        for name, file, count in (("HDL", ROOT / "examples/test.hdl", 1),
                                  ("Jack", ROOT / "tests/fixtures/jack/nested.jack", 5)):
            tree = self.parse(name, file.read_text(encoding="utf-8"))
            captures = self.captures(name, "indents.scm", tree)
            self.assertEqual(len(captures["indent"]), count)
            self.assertEqual(len(captures["end"]), count)
            for block in captures["indent"]:
                self.assertGreater(block.end_point.row, block.start_point.row)
                self.assertTrue(any(end.end_byte <= block.end_byte and end.start_byte >= block.start_byte
                                    for end in captures["end"]))

    def test_missing_snippet_registration_rejected(self):
        invalid = copy.deepcopy(self.manifest)
        invalid["snippets"] = invalid["snippets"][:-1]
        with self.assertRaisesRegex(ValueError, "registered"):
            validate_layout(ROOT, invalid)

    def test_missing_grammar_reference_rejected(self):
        invalid = copy.deepcopy(self.manifest)
        del invalid["grammars"]["jack"]
        with self.assertRaisesRegex(ValueError, "unregistered grammar"):
            validate_layout(ROOT, invalid)

    def test_unpinned_grammar_rejected(self):
        invalid = copy.deepcopy(self.manifest)
        invalid["grammars"]["hdl"]["rev"] = "main"
        with self.assertRaisesRegex(ValueError, "full commit SHA"):
            validate_layout(ROOT, invalid)

    def test_missing_resource_rejected(self):
        invalid = copy.deepcopy(self.manifest)
        invalid["snippets"].append("snippets/missing.json")
        with self.assertRaisesRegex(ValueError, "Missing resource"):
            validate_layout(ROOT, invalid)

    def test_hdl_block_comment(self):
        self.parse("HDL", self.hdl_fixtures["block-comment"])

    def test_hdl_indexed_part_pin(self):
        self.parse("HDL", self.hdl_fixtures["indexed-part-pin"])

    def test_hdl_bus_range(self):
        self.parse("HDL", self.hdl_fixtures["bus-range"])

    def test_hdl_ranges_are_not_width_declarations(self):
        tree = Parser(self.languages["HDL"]).parse(b"CHIP Sample { IN bus[0..7]; OUT out; PARTS: }")
        self.assertTrue(tree.root_node.has_error, "Header buses declare a width, not a range")


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--hdl-source", type=Path, help="Test a separate upstream HDL checkout; all HDL regressions must pass")
    options = args.parse_args()
    manifest = read_toml(ROOT / "extension.toml")
    configs = validate_layout(ROOT, manifest)
    # Missing fixtures are setup errors, never expected parser failures.
    ExtensionTests.hdl_fixtures = {
        name: resource(ROOT, f"tests/fixtures/hdl/{name}.hdl").read_text(encoding="utf-8")
        for name in HDL_REGRESSIONS
    }
    if not shutil.which("git"):
        raise RuntimeError("Install Git and put it on PATH")
    # Windows keeps loaded DLLs locked until this process exits. Failed DLL
    # cleanup is harmless in OS temp storage; Unix removes the directory.
    temporary = tempfile.TemporaryDirectory(prefix="nand2tetris-validation-", ignore_cleanup_errors=True)
    with temporary as folder:
        work = Path(folder)
        languages, libraries = {}, []
        for name, (_, config) in configs.items():
            grammar_name = config["grammar"]
            grammar = manifest["grammars"][grammar_name]
            source = work / grammar_name
            if grammar_name == "hdl" and options.hdl_source:
                source = options.hdl_source.resolve()
                print(f"HDL source override: {source}", flush=True)
            else:
                run("git", "init", "--quiet", str(source))
                run("git", "-C", str(source), "fetch", "--quiet", "--depth=1", grammar["repository"], grammar["rev"])
                run("git", "-C", str(source), "checkout", "--quiet", "--detach", "FETCH_HEAD")
                if run("git", "-C", str(source), "rev-parse", "HEAD") != grammar["rev"]:
                    raise RuntimeError(f"Fetched revision mismatch for {grammar_name}")
            languages[name], library = build_language(grammar_name, source, work)
            libraries.append(library)
            origin = str(source) if grammar_name == "hdl" and options.hdl_source else grammar["rev"]
            print(f"Built {name}: {origin}", flush=True)
        ExtensionTests.manifest = manifest
        ExtensionTests.configs = configs
        ExtensionTests.languages = languages
        known_hdl = manifest["grammars"]["hdl"]["rev"] == HDL_KNOWN_REV and options.hdl_source is None
        for regression in HDL_REGRESSIONS:
            method = getattr(ExtensionTests, "test_hdl_" + regression.replace("-", "_"))
            method.__unittest_expecting_failure__ = known_hdl
        if known_hdl:
            print(f"Known HDL parser failures at {HDL_KNOWN_REV}: {', '.join(HDL_REGRESSIONS)}", flush=True)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExtensionTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        sys.exit(f"Validation setup failed: {error}")
