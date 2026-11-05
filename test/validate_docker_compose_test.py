import importlib.util
import io
import json
import pathlib
import tempfile
import textwrap
import unittest
from unittest import mock

path = pathlib.Path(__file__).parent.parent / "hooks/validate-docker-compose/validate-docker-compose.py"
spec = importlib.util.spec_from_file_location("vdc", path)
vdc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vdc)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        p = self.dir / name
        p.write_text(textwrap.dedent(text))
        return p

    def check(self, compose, example=None, **files):
        self.write("docker-compose.yml", compose)
        if example is not None:
            self.write(".env.example", example)
        for name, text in files.items():
            self.write(name.replace("__", "."), text)
        return vdc.run([str(self.dir)], use_docker=False)

    def codes(self, findings):
        return sorted(f["code"] for f in findings)


PINNED = "services:\n  db:\n    image: ${POSTGRES_IMAGE:?POSTGRES_IMAGE is required}\n"


class Images(Base):
    def test_pinned_variable_passes(self):
        self.assertEqual(self.check(PINNED, "POSTGRES_IMAGE=postgres:18.6.1-trixie\n"), [])

    def test_hardcoded_image(self):
        found = self.check("services:\n  db:\n    image: postgres:18.6\n", "")
        self.assertEqual(self.codes(found), ["E1"])
        self.assertIn("${DB_IMAGE:?", found[0]["message"])

    def test_latest_floating_no_tag_and_major_only(self):
        for value in ("postgres:latest", "postgres:stable", "postgres", "postgres:18", "redis:alpine"):
            with self.subTest(value=value):
                found = self.check(PINNED, f"POSTGRES_IMAGE={value}\n")
                self.assertEqual(self.codes(found), ["E4"])

    def test_missing_patch_is_a_warning(self):
        found = self.check(PINNED, "POSTGRES_IMAGE=python:3.14-slim-trixie\n")
        self.assertEqual([(f["level"], f["code"]) for f in found], [("WARNING", "W1")])

    def test_digest_and_dated_tags_pass(self):
        digest = "postgres@sha256:" + "a" * 64
        for value in (digest, "postgres:18.6@sha256:" + "b" * 64, "minio/minio:RELEASE.2024-01-16T16-07-38Z"):
            with self.subTest(value=value):
                self.assertEqual(self.check(PINNED, f"POSTGRES_IMAGE={value}\n"), [])

    def test_registry_port_is_not_a_tag(self):
        found = self.check(PINNED, "POSTGRES_IMAGE=registry.local:5000/postgres\n")
        self.assertEqual(self.codes(found), ["E4"])

    def test_wrong_variable_forms(self):
        for image in ("${POSTGRES_IMAGE:-postgres:18.6}", "${POSTGRES_IMAGE}", "postgres:${PG_TAG:?x}",
                      "$POSTGRES_IMAGE"):
            with self.subTest(image=image):
                found = self.check(f"services:\n  db:\n    image: \"{image}\"\n", "POSTGRES_IMAGE=postgres:18.6\n")
                self.assertIn("E2", self.codes(found))
                self.assertNotIn("E3", self.codes(found))


class EnvExample(Base):
    def test_missing_declaration(self):
        self.assertEqual(self.codes(self.check(PINNED, "OTHER=1\n")), ["E3"])

    def test_missing_file(self):
        self.assertEqual(self.codes(self.check(PINNED)), ["E3"])

    def test_unused_image_variable_warns(self):
        found = self.check(PINNED, "POSTGRES_IMAGE=postgres:18.6.1\nREDIS_IMAGE=redis:8.2.2\n")
        self.assertEqual(self.codes(found), ["W2"])

    def test_env_differs_warns_without_leaking_other_values(self):
        found = self.check(PINNED, "POSTGRES_IMAGE=postgres:18.6.1\n",
                           __env="POSTGRES_IMAGE=postgres:18.5.0\nDB_PASSWORD=hunter2\n")
        self.assertEqual(self.codes(found), ["W3"])
        self.assertNotIn("hunter2", json.dumps(found))


class Builds(Base):
    def test_build_only(self):
        self.assertEqual(self.check("services:\n  api:\n    build: .\n", ""), [])

    def test_build_with_literal_output_tag(self):
        self.assertEqual(self.check("services:\n  api:\n    build: .\n    image: myapi:local\n", ""), [])

    def test_build_in_base_image_in_override(self):
        found = self.check("services:\n  api:\n    build: .\n", "",
                           **{"docker-compose__override__yml": "services:\n  api:\n    image: myapi:dev\n"})
        self.assertEqual(found, [])


class Structure(Base):
    def test_multiple_services(self):
        compose = """\
        services:
          db:
            image: ${POSTGRES_IMAGE:?required}
          cache:
            image: redis:8.2.2
          api:
            build: .
        """
        found = self.check(compose, "POSTGRES_IMAGE=postgres:18.6.1\n")
        self.assertEqual([(f["code"], f["service"]) for f in found], [("E1", "cache")])

    def test_anchors_and_merge_keys(self):
        compose = """\
        x-db: &db
          image: ${POSTGRES_IMAGE:?required}
          restart: unless-stopped
        services:
          primary:
            <<: *db
          replica:
            <<: *db
            image: postgres:latest
        """
        found = self.check(compose, "POSTGRES_IMAGE=postgres:18.6.1\n")
        self.assertEqual([(f["code"], f["service"]) for f in found], [("E1", "replica")])

    def test_several_variables(self):
        compose = """\
        services:
          db:
            image: ${POSTGRES_IMAGE:?required}
          agent:
            image: ${INFISICAL_CLI_IMAGE:?required}
        """
        found = self.check(compose, "POSTGRES_IMAGE=postgres:18.6.1\nINFISICAL_CLI_IMAGE=infisical/cli:latest\n")
        self.assertEqual([(f["code"], f["service"]) for f in found], [("E4", "agent")])

    def test_invalid_yaml(self):
        self.assertEqual(self.codes(self.check("services: [\n", "")), ["E5"])

    def test_skips_other_yaml(self):
        self.write("config.yml", "image: postgres:latest\n")
        self.assertEqual(vdc.run([str(self.dir)], use_docker=False), [])


class Hook(Base):
    def run_hook(self, file_path):
        stdin = io.StringIO(json.dumps({"tool_input": {"file_path": str(file_path)}}))
        stderr = io.StringIO()
        with mock.patch("sys.stdin", stdin), mock.patch("sys.stderr", stderr), \
                mock.patch.object(vdc, "docker_compose", return_value=None):
            return vdc.main(["--hook"]), stderr.getvalue()

    def test_blocks_compose_edit_with_errors(self):
        p = self.write("docker-compose.yml", "services:\n  db:\n    image: postgres:latest\n")
        code, err = self.run_hook(p)
        self.assertEqual(code, 2)
        self.assertIn("E1", err)

    def test_env_example_edit_revalidates_folder(self):
        self.write("docker-compose.yml", PINNED)
        p = self.write(".env.example", "POSTGRES_IMAGE=postgres:latest\n")
        self.assertEqual(self.run_hook(p)[0], 2)

    def test_clean_and_unrelated_files_pass(self):
        self.write("docker-compose.yml", PINNED)
        self.write(".env.example", "POSTGRES_IMAGE=postgres:18.6.1\n")
        self.assertEqual(self.run_hook(self.dir / "docker-compose.yml"), (0, ""))
        self.assertEqual(self.run_hook(self.write("app.py", "x = 1\n"))[0], 0)

    def test_warnings_do_not_block(self):
        self.write("docker-compose.yml", PINNED)
        p = self.write(".env.example", "POSTGRES_IMAGE=postgres:18.6\n")
        self.assertEqual(self.run_hook(p)[0], 0)



class DockerCheck(Base):
    def test_compose_config_failure_is_e5(self):
        self.write("docker-compose.yml", PINNED)
        self.write("docker-compose.prod.yml", PINNED)
        self.write(".env.example", "POSTGRES_IMAGE=postgres:18.6.1\n")
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            return mock.Mock(returncode=1, stderr="service \"db\" has neither an image nor a build\n")

        with mock.patch.object(vdc, "docker_compose", return_value=["docker", "compose"]), \
                mock.patch.object(vdc.subprocess, "run", side_effect=fake_run):
            found = vdc.run([str(self.dir)], use_docker=True)
        self.assertEqual(self.codes(found), ["E5", "E5"])
        self.assertIn("--env-file", calls[0])
        self.assertEqual(sum(a.count("-f") for a in calls), 3)  # base alone, then base + prod


if __name__ == "__main__":
    unittest.main()
