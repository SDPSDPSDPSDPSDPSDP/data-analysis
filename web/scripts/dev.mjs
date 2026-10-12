// Runs next dev and rebuilds the wheel and docstrings whenever shirin/ changes,
// so Python edits reach the browser without restarting the dev server.
import { execSync, spawn } from "node:child_process";
import { watch } from "node:fs";

const REBUILD = "node scripts/build-wheel.mjs && uv run python scripts/docstrings.py lib/docstrings.json";

let timer;
watch("../shirin", { recursive: true }, (_event, file) => {
  if (!file?.endsWith(".py")) return;
  clearTimeout(timer);
  // One save can fire several events; wait for them to settle.
  timer = setTimeout(() => {
    console.log(`\n[wheel] ${file} changed, rebuilding...`);
    try {
      execSync(REBUILD, { stdio: "inherit" });
      console.log("[wheel] rebuilt, hard reload the page");
    } catch {
      console.error("[wheel] REBUILD FAILED, browser still runs the previous wheel");
    }
  }, 300);
});

const next = spawn("next dev --port 6817", { stdio: "inherit", shell: true });
next.on("exit", (code) => process.exit(code ?? 1));
