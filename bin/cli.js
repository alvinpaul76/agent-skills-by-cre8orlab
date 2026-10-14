#!/usr/bin/env node
"use strict";

// Installs a Claude Code hook from this repo's hooks/ folder into ~/.claude.
// Zero dependencies. Each hook folder holds hook.json plus the script it names.

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const REPO_ROOT = path.resolve(__dirname, "..");
const HOOKS_SRC = path.join(REPO_ROOT, "hooks");
const CLAUDE = path.join(os.homedir(), ".claude");
const HOOKS_DEST = path.join(CLAUDE, "hooks");
const SETTINGS = path.join(CLAUDE, "settings.json");

function say(s) { process.stdout.write(s + "\n"); }
function fail(s) { process.stderr.write("Error: " + s + "\n"); process.exit(1); }

function availableHooks() {
  if (!fs.existsSync(HOOKS_SRC)) return [];
  return fs.readdirSync(HOOKS_SRC, { withFileTypes: true })
    .filter(e => e.isDirectory() && fs.existsSync(path.join(HOOKS_SRC, e.name, "hook.json")))
    .map(e => e.name);
}

function loadHook(name) {
  if (!name || !availableHooks().includes(name)) {
    fail(`Unknown hook "${name || ""}". Available: ${availableHooks().join(", ") || "none"}.`);
  }
  const dir = path.join(HOOKS_SRC, name);
  const spec = JSON.parse(fs.readFileSync(path.join(dir, "hook.json"), "utf8"));
  const scriptSrc = path.join(dir, spec.script);
  if (!fs.existsSync(scriptSrc)) fail(`Package is incomplete: ${spec.script} is missing.`);
  return {
    event: spec.event,
    matcher: spec.matcher,
    script: spec.script,
    scriptSrc,
    scriptDest: path.join(HOOKS_DEST, spec.script),
    command: `python3 "$HOME/.claude/hooks/${spec.script}" ${spec.args}`.trim(),
  };
}

function readSettings() {
  try { return JSON.parse(fs.readFileSync(SETTINGS, "utf8")); }
  catch (e) {
    if (e.code === "ENOENT") return {};
    fail(`Cannot parse ${SETTINGS}: ${e.message}. No changes made.`);
  }
}

function backup(file) {
  if (!fs.existsSync(file)) return null;
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const dest = `${file}.backup-${stamp}`;
  fs.copyFileSync(file, dest, fs.constants.COPYFILE_EXCL);
  return dest;
}

function writeSettings(settings) {
  fs.mkdirSync(CLAUDE, { recursive: true });
  const temp = `${SETTINGS}.tmp-${process.pid}`;
  fs.writeFileSync(temp, JSON.stringify(settings, null, 2) + "\n", { mode: 0o600 });
  fs.renameSync(temp, SETTINGS);
}

// A hook entry is ours only when its command is exactly the one we install.
function isOurs(h, hook) {
  return h?.command === hook.command;
}

function hasOurs(settings, hook) {
  const entries = settings?.hooks?.[hook.event];
  return Array.isArray(entries) && entries.some(e =>
    Array.isArray(e.hooks) && e.hooks.some(h => isOurs(h, hook)));
}

function isConfigured(settings, hook) {
  const entries = settings?.hooks?.[hook.event];
  return Array.isArray(entries) && entries.some(e =>
    e.matcher === hook.matcher && Array.isArray(e.hooks) && e.hooks.some(h => isOurs(h, hook)));
}

function install(name) {
  const hook = loadHook(name);
  const settings = readSettings();
  const alreadyConfigured = isConfigured(settings, hook);

  fs.mkdirSync(HOOKS_DEST, { recursive: true });
  const scriptBackup = fs.existsSync(hook.scriptDest) &&
    !fs.readFileSync(hook.scriptDest).equals(fs.readFileSync(hook.scriptSrc))
    ? backup(hook.scriptDest) : null;
  fs.copyFileSync(hook.scriptSrc, hook.scriptDest);
  fs.chmodSync(hook.scriptDest, 0o700);

  let settingsBackup = null;
  if (!alreadyConfigured) {
    settingsBackup = backup(SETTINGS);
    settings.hooks = settings.hooks || {};
    if (!Array.isArray(settings.hooks[hook.event])) settings.hooks[hook.event] = [];
    settings.hooks[hook.event].push({
      matcher: hook.matcher,
      hooks: [{ type: "command", command: hook.command }],
    });
    writeSettings(settings);
  }

  say(`Installed hook: ${name}`);
  say(`Script:   ${hook.scriptDest}`);
  say(`Settings: ${SETTINGS}${alreadyConfigured ? " (already configured, unchanged)" : ""}`);
  if (settingsBackup) say(`Settings backup: ${settingsBackup}`);
  if (scriptBackup) say(`Previous script backup: ${scriptBackup}`);
  say("");
  say("Next: restart Claude Code, check /hooks, then run a noisy command such as npm install.");
}

function uninstall(name) {
  const hook = loadHook(name);
  const settings = readSettings();
  const entries = settings?.hooks?.[hook.event];
  let settingsBackup = null;

  if (hasOurs(settings, hook)) {
    const kept = entries
      .map(e => Array.isArray(e.hooks) ? { ...e, hooks: e.hooks.filter(h => !isOurs(h, hook)) } : e)
      .filter(e => !Array.isArray(e.hooks) || e.hooks.length > 0);
    settingsBackup = backup(SETTINGS);
    if (kept.length) settings.hooks[hook.event] = kept;
    else delete settings.hooks[hook.event];
    if (Object.keys(settings.hooks).length === 0) delete settings.hooks;
    writeSettings(settings);
  }
  if (fs.existsSync(hook.scriptDest)) fs.unlinkSync(hook.scriptDest);

  say(`Uninstalled hook: ${name}`);
  if (settingsBackup) say(`Settings backup: ${settingsBackup}`);
  say("Other settings and hooks were left untouched.");
}

function status(name) {
  const hook = loadHook(name);
  const script = fs.existsSync(hook.scriptDest);
  const configured = isConfigured(readSettings(), hook);
  say(`Script: ${script ? "installed" : "missing"}`);
  say(`Config: ${configured ? "configured" : "not configured"}`);
  if (!(script && configured)) process.exitCode = 1;
}

function help() {
  const names = availableHooks();
  say("cre8orlab hook installer");
  say("");
  say("Usage:");
  say("  npx github:alvinpaul76/agent-skills-by-cre8orlab install <hook>");
  say("  npx github:alvinpaul76/agent-skills-by-cre8orlab status <hook>");
  say("  npx github:alvinpaul76/agent-skills-by-cre8orlab uninstall <hook>");
  say("");
  say(`Hooks: ${names.join(", ") || "none"}`);
}

const [cmd, name] = process.argv.slice(2);
if (cmd === "install") install(name);
else if (cmd === "uninstall") uninstall(name);
else if (cmd === "status") status(name);
else help();
