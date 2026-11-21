/**
 * omp adapter for the shared project safeguards in `.agents/hooks/`.
 *
 * omp skips Claude Code and Codex hook registrations, so this factory runs the same Python hooks
 * through `.agents/hooks/run.sh`, with the payload shape those clients send
 * (`hook_event_name`, `tool_name`, `tool_input`, `cwd`):
 *
 * | omp event     | omp tools               | hook                                  |
 * |---------------|-------------------------|---------------------------------------|
 * | `tool_call`   | `edit`, `write`, `ast_edit` | `protect_paths.py`                |
 * | `tool_call`   | `bash`                  | `guard_bash.py`, `pre_commit_lint.py` |
 * | `tool_result` | `edit`, `write`, `ast_edit` | `validate_gdscript.py`            |
 *
 * A pre-tool deny blocks the call with the hook's reason. A post-tool block cannot undo the edit, so
 * its reason is fed back to the agent as context, as Claude Code does. A hook that cannot run (no
 * bash, no Python) allows the call and warns once, matching the other clients' fail-open boundary.
 */
import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks";
import * as fs from "node:fs";
import * as path from "node:path";

const RUN_SH = path.resolve(import.meta.dir, "..", "..", "..", ".agents", "hooks", "run.sh");
/** omp tool name -> the tool name the shared hooks expect. */
const WRITE_TOOLS: Record<string, string> = { edit: "Edit", write: "Write" };
/** Below omp's 30 s `tool_call` budget, which fails closed. */
const HOOK_TIMEOUT_MS = 25_000;

type HookOutcome = { kind: "ok"; output: Record<string, unknown> | null } | { kind: "failed"; detail: string };

/** On Windows the first `bash` on PATH is often WSL's or the Store alias; the hooks need Git's. */
function findBash(): string {
	if (process.platform !== "win32") return "bash";
	const git = Bun.which("git");
	const candidates = [
		git && path.resolve(path.dirname(git), "..", "bin", "bash.exe"),
		git && path.resolve(path.dirname(git), "..", "..", "bin", "bash.exe"),
		process.env.ProgramFiles && path.join(process.env.ProgramFiles, "Git", "bin", "bash.exe"),
	];
	return candidates.find((candidate): candidate is string => !!candidate && fs.existsSync(candidate)) ?? "bash";
}

const BASH = findBash();

function parseOutput(stdout: string): Record<string, unknown> | null {
	const lines = stdout.trim().split(/\r?\n/).filter(Boolean);
	for (let i = lines.length - 1; i >= 0; i--) {
		try {
			const value: unknown = JSON.parse(lines[i]);
			if (value && typeof value === "object") return value as Record<string, unknown>;
		} catch {
			// Not the JSON line; keep looking.
		}
	}
	return null;
}

async function runHook(script: string, payload: Record<string, unknown>, cwd: string): Promise<HookOutcome> {
	const env = { ...process.env };
	// The hooks resolve the repository from CLAUDE_PROJECT_DIR first; let the payload's cwd decide.
	delete env.CLAUDE_PROJECT_DIR;
	try {
		const proc = Bun.spawn([BASH, RUN_SH, script], { cwd, env, stdin: "pipe", stdout: "pipe", stderr: "pipe" });
		proc.stdin.write(JSON.stringify(payload));
		proc.stdin.end();
		const timer = setTimeout(() => proc.kill(), HOOK_TIMEOUT_MS);
		const [stdout, stderr, code] = await Promise.all([
			new Response(proc.stdout).text(),
			new Response(proc.stderr).text(),
			proc.exited,
		]);
		clearTimeout(timer);
		if (code !== 0) return { kind: "failed", detail: (stderr.trim() || `exit code ${code}`).slice(0, 500) };
		return { kind: "ok", output: parseOutput(stdout) };
	} catch (error) {
		return { kind: "failed", detail: `could not run ${BASH}: ${String(error)}` };
	}
}

function denyReason(output: Record<string, unknown> | null): string | null {
	const specific = output?.hookSpecificOutput as Record<string, unknown> | undefined;
	if (specific?.permissionDecision !== "deny") return null;
	return String(specific.permissionDecisionReason ?? "Blocked by a project safeguard.");
}

function postBlockReason(output: Record<string, unknown> | null): string | null {
	if (output?.decision !== "block") return null;
	return String(output.reason ?? "A project validation hook failed.");
}

export default function projectSafeguards(pi: HookAPI): void {
	let warned = false;
	const failOpen = (ctx: { ui?: { notify?: (message: string, type?: string) => void } }, script: string, detail: string) => {
		pi.logger?.warn?.(`project safeguard ${script} did not run: ${detail}`);
		if (warned) return;
		warned = true;
		ctx.ui?.notify?.(`Project safeguard ${script} did not run (allowed): ${detail}`, "warning");
	};

	const preTool = (script: string, toolNames: Record<string, string>) => {
		pi.on("tool_call", async (event, ctx) => {
			const toolName = toolNames[event.toolName];
			if (!toolName) return;
			// The bash tool's own `cwd` argument, else the session's directory.
			const cwd =
				typeof event.input.cwd === "string" && event.input.cwd ? path.resolve(ctx.cwd, event.input.cwd) : ctx.cwd;
			const payload = { hook_event_name: "PreToolUse", tool_name: toolName, tool_input: event.input, cwd };
			const outcome = await runHook(script, payload, cwd);
			if (outcome.kind === "failed") return failOpen(ctx, script, outcome.detail);
			const reason = denyReason(outcome.output);
			if (reason) return { block: true, reason: `${script}: ${reason}` };
		});
	};

	preTool("protect_paths.py", WRITE_TOOLS);
	preTool("guard_bash.py", { bash: "Bash" });
	preTool("pre_commit_lint.py", { bash: "Bash" });

	pi.on("tool_result", async (event, ctx) => {
		const toolName = WRITE_TOOLS[event.toolName];
		if (!toolName || event.isError) return;
		const payload = { hook_event_name: "PostToolUse", tool_name: toolName, tool_input: event.input, cwd: ctx.cwd };
		const outcome = await runHook("validate_gdscript.py", payload, ctx.cwd);
		if (outcome.kind === "failed") return failOpen(ctx, "validate_gdscript.py", outcome.detail);
		const reason = postBlockReason(outcome.output);
		if (reason) return { additionalContext: reason };
	});
}
