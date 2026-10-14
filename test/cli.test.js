"use strict";
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const CLI = path.join(__dirname, "..", "bin", "cli.js");
const HOOK = "quiet-command-output";

function setup() {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), "hooks-test-"));
  const run = cmd => spawnSync("node", [CLI, cmd, HOOK], { env: { ...process.env, HOME: home }, encoding: "utf8" });
  const settingsPath = path.join(home, ".claude", "settings.json");
  const settings = () => JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  return { home, run, settingsPath, settings };
}

test("install is idempotent and status reports it", () => {
  const { run, settings } = setup();
  assert.strictEqual(run("install").status, 0);
  assert.strictEqual(run("install").status, 0);
  assert.strictEqual(settings().hooks.PreToolUse.length, 1);
  assert.strictEqual(run("status").status, 0);
});

test("uninstall removes our entry even if the matcher was changed, keeps others", () => {
  const { run, settings, settingsPath } = setup();
  run("install");
  const s = settings();
  s.hooks.PreToolUse[0].matcher = "Bash|Edit";
  s.hooks.PreToolUse.push({ matcher: "Bash", hooks: [{ type: "command", command: "echo mentions quiet-command-output.py" }] });
  fs.writeFileSync(settingsPath, JSON.stringify(s));
  assert.strictEqual(run("uninstall").status, 0);
  const after = settings().hooks.PreToolUse;
  assert.strictEqual(after.length, 1);
  assert.match(after[0].hooks[0].command, /^echo mentions/);
});
