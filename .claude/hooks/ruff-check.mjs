// PostToolUse: lint an edited .py file with ruff. Exit 2 feeds the errors back to Claude.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(0, "utf8"));
const file = input.tool_input?.file_path ?? input.tool_response?.filePath;
if (!file || !file.endsWith(".py")) process.exit(0);

// --system-certs: local TLS interception breaks uv's bundled certs (see AGENTS.md Commands).
const result = spawnSync("uv", ["run", "--system-certs", "ruff", "check", file], {
  cwd: process.env.CLAUDE_PROJECT_DIR,
  encoding: "utf8",
  shell: process.platform === "win32",
});
if (result.status !== 0) {
  process.stderr.write(`ruff check failed for ${file}:\n${result.stdout}${result.stderr}`);
  process.exit(2);
}
