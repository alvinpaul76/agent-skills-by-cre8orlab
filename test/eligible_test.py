import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).parent.parent / "hooks/quiet-command-output/quiet-command-output.py"
spec = importlib.util.spec_from_file_location("qco", path)
qco = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qco)


class Eligible(unittest.TestCase):
    def test_wraps_listed_commands(self):
        for cmd in ("npm install", "pytest -k ignore_me", "pytest tests/test_login.py", "cargo test"):
            self.assertTrue(qco.eligible(cmd), cmd)

    def test_skips_interactive_words(self):
        for cmd in ("npm test --watch", "pytest -i", "npm install login"):
            self.assertFalse(qco.eligible(cmd), cmd)


if __name__ == "__main__":
    unittest.main()
