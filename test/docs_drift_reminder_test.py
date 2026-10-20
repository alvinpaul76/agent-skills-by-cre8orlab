import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).parent.parent / "hooks/docs-drift-reminder/docs-drift-reminder.py"
spec = importlib.util.spec_from_file_location("ddr", path)
ddr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ddr)

ROOT = pathlib.Path("/work/project")


class IsAppSource(unittest.TestCase):
    def test_python_files_under_app(self):
        for f in ("/work/project/app/main.py", "/work/project/app/api/v1/spam.py"):
            self.assertTrue(ddr.is_app_source(f, ROOT), f)

    def test_other_files_are_ignored(self):
        for f in ("/work/project/README.md", "/work/project/tests/app/test_x.py",
                  "/work/project/app/notes.txt", "/work/other/app/main.py"):
            self.assertFalse(ddr.is_app_source(f, ROOT), f)


if __name__ == "__main__":
    unittest.main()
