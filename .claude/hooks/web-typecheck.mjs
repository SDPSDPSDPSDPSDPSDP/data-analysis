// Stop: typecheck web/ when its TypeScript changed. Exit 2 makes Claude fix the errors before stopping.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const input = JSON.parse(readFileSync(0, "utf8"));
// Already continuing because of this hook: do not loop forever on errors Claude cannot fix.
if (input.stop_hook_active) process.exit(0);

const root = process.env.CLAUDE_PROJECT_DIR;
const status = spawnSync("git", ["status", "--porcelain", "--untracked-files=all", "--", "web"], { cwd: root, encoding: "utf8" });
if (status.status !== 0) {
  process.stderr.write(`git status failed: ${status.stderr}`);
  process.exit(1);
}
const tsChanged = status.stdout.split("\n").some((line) => /\.(ts|tsx)$/.test(line.trim()));
if (!tsChanged) process.exit(0);

const tsc = spawnSync("npx", ["tsc", "--noEmit"], {
  cwd: join(root, "web"),
  encoding: "utf8",
  shell: process.platform === "win32",
});
if (tsc.status !== 0) {
  process.stderr.write(`web typecheck failed:\n${tsc.stdout}${tsc.stderr}`);
  process.exit(2);
}
