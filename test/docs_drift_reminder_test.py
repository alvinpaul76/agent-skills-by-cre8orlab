import importlib.util
import os
import tempfile
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


class IsSource(unittest.TestCase):
    def test_source_files(self):
        for f in ("/work/project/src/index.ts", "/work/project/main.go",
                  "/work/project/app/main.py"):
            self.assertTrue(ddr.is_source(f, ROOT), f)

    def test_docs_and_non_source_are_ignored(self):
        for f in ("/work/project/README.md", "/work/project/docs/conf.py",
                  "/work/project/package-lock.json", "/work/other/src/index.ts"):
            self.assertFalse(ddr.is_source(f, ROOT), f)


class OncePerSession(unittest.TestCase):
    def test_second_call_is_false(self):
        sid = f"test-{os.getpid()}"
        marker = pathlib.Path(tempfile.gettempdir()) / f"docs-drift-reminder-{sid}"
        marker.unlink(missing_ok=True)
        self.addCleanup(lambda: marker.unlink(missing_ok=True))
        self.assertTrue(ddr.first_time_this_session(sid))
        self.assertFalse(ddr.first_time_this_session(sid))


if __name__ == "__main__":
    unittest.main()
