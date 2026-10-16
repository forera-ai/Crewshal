"""Check the entry against inherited bytes and CPython locale changes."""

import ast
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal.linux_batch_entry import observer_entry_source


class EmptyEntryTests(unittest.TestCase):
    def entries(self):
        root = Path(__file__).resolve().parents[2]
        paths = (
            "scripts/phase_2d_owner_input_upload.py",
            "scripts/phase_2d_owner_capabilities.py",
            "src/crewshal/linux_parent_entry.py",
            "src/crewshal/linux_batch_entry.py",
            "src/crewshal/linux_qualification_fixture.py",
        )
        sources = [(name, (root / name).read_text()) for name in paths]
        sources.append(("observer-entry.py", observer_entry_source().decode()))
        for name, source in sources:
            nodes = [
                node
                for node in ast.walk(ast.parse(source))
                if isinstance(node, ast.If)
                and isinstance(node.test, ast.Attribute)
                and ast.unparse(node.test) == "os.environ"
            ]
            self.assertEqual(len(nodes), 1, name)
            yield (
                name,
                compile(
                    ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), name, "exec"
                ),
            )

    def execute(self, code, environment, inherited, isolated=True):
        namespace = {
            "os": SimpleNamespace(environ=environment),
            "sys": SimpleNamespace(
                platform="linux",
                flags=SimpleNamespace(isolated=isolated, no_site=True, dont_write_bytecode=True),
            ),
        }
        with patch("builtins.open", return_value=io.BytesIO(inherited)) as opened:
            exec(code, namespace)
        return opened

    def test_only_generated_locale_with_empty_kernel_bytes_is_removed(self):
        for name, code in self.entries():
            with self.subTest(entry=name):
                environment = {"LC_CTYPE": "C.UTF-8"}
                opened = self.execute(code, environment, b"")
                self.assertEqual(environment, {})
                opened.assert_called_once_with("/proc/self/environ", "rb")

    def test_inherited_locale_other_values_and_nonisolated_start_are_refused(self):
        cases = (
            ({"LC_CTYPE": "C.UTF-8"}, b"LC_CTYPE=C.UTF-8\0", True),
            ({"TOKEN": "private"}, b"", True),
            ({"LC_CTYPE": "C"}, b"", True),
            ({"LC_CTYPE": "C.UTF-8"}, b"", False),
        )
        for name, code in self.entries():
            for environment, inherited, isolated in cases:
                with self.subTest(entry=name, environment=tuple(environment)):
                    with self.assertRaises(ValueError):
                        self.execute(code, environment.copy(), inherited, isolated)

    def test_empty_environment_does_not_open_proc(self):
        for name, code in self.entries():
            with self.subTest(entry=name):
                self.execute(code, {}, b"").assert_not_called()
