#!/usr/bin/env node
// Plays a prototype's rules headless, for AI playtesters and solvers without a browser.
//
//   node proto_cli.mjs <prototype.html>                 interactive: describe, actions, act <name>, quit
//   node proto_cli.mjs <prototype.html> "act left" ...  runs the commands in order, then exits
//   node proto_cli.mjs --no-tutorial <prototype.html>   starts cold, skipping the tutorial
//
// The prototype keeps its rules and window.proto in one <script id="proto-rules"> block that never
// touches the page; that block runs here in a sandbox with no DOM.
import { readFileSync } from "node:fs";
import readline from "node:readline";
import vm from "node:vm";

const args = process.argv.slice(2);
const cold = args.includes("--no-tutorial");
const [file, ...commands] = args.filter((arg) => arg !== "--no-tutorial");
if (!file) {
  console.error("usage: node proto_cli.mjs [--no-tutorial] <prototype.html> [command ...]");
  process.exit(2);
}

let html;
try {
  html = readFileSync(file, "utf8");
} catch (error) {
  console.error(`can't read ${file}: ${error.code ?? error.message}`);
  process.exit(2);
}
const block = html.match(/<script\b[^>]*\bid=["']proto-rules["'][^>]*>([\s\S]*?)<\/script>/i);
if (!block) {
  console.error(`no <script id="proto-rules"> block in ${file}`);
  process.exit(2);
}

const sandbox = { console, Math, Date, JSON };
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
try {
  vm.runInContext(block[1], sandbox, { filename: `${file}#proto-rules` });
} catch (error) {
  console.error(`the rules block failed to run without a page: ${error.message}`);
  process.exit(2);
}

const proto = sandbox.proto;
if (!proto || ["describe", "actions", "act"].some((name) => typeof proto[name] !== "function")) {
  console.error("the rules block must define window.proto with describe(), actions() and act(name)");
  process.exit(2);
}
if (cold) {
  if (typeof proto.restart !== "function") {
    console.error("--no-tutorial needs window.proto.restart({ tutorial }) in the rules block");
    process.exit(2);
  }
  proto.restart({ tutorial: false });
}

function show(value) {
  console.log(Array.isArray(value) ? value.join("\n") : String(value));
}

// Returns false when the session should end.
function run(line) {
  const command = line.trim();
  if (!command) return true;
  if (command === "quit" || command === "exit") return false;
  if (command === "describe" || command === "look") show(proto.describe());
  else if (command === "actions") show(proto.actions());
  else show(proto.act(command.startsWith("act ") ? command.slice(4).trim() : command));
  return true;
}

if (commands.length > 0) {
  for (const command of commands) {
    console.log(`> ${command}`);
    if (!run(command)) break;
  }
  process.exit(0);
}

show(proto.describe());
console.log(`\nactions: ${proto.actions().join(", ")}`);
const rl = readline.createInterface({ input: process.stdin, output: process.stdout, prompt: "> " });
rl.prompt();
rl.on("line", (line) => {
  if (!run(line)) {
    rl.close();
    return;
  }
  rl.prompt();
});
rl.on("close", () => process.exit(0));
