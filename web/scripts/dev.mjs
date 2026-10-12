// Runs next dev and rebuilds the wheel, docstrings and previews whenever shirin/ changes,
// and the previews whenever an example changes, without restarting the dev server.
import { execSync, spawn } from "node:child_process";
import { watch } from "node:fs";

const PREVIEWS = "node scripts/build-previews.mjs";
const REBUILD = `node scripts/build-wheel.mjs && uv run python scripts/docstrings.py lib/docstrings.json && ${PREVIEWS}`;

function watchPython(dir, command, label) {
  let timer;
  watch(dir, { recursive: true }, (_event, file) => {
    if (!file?.endsWith(".py")) return;
    clearTimeout(timer);
    // One save can fire several events; wait for them to settle.
    timer = setTimeout(() => {
      console.log(`\n[${label}] ${file} changed, rebuilding...`);
      try {
        execSync(command, { stdio: "inherit" });
        console.log(`[${label}] rebuilt, hard reload the page`);
      } catch {
        console.error(`[${label}] REBUILD FAILED, browser still runs the previous build`);
      }
    }, 300);
  });
}

watchPython("../shirin", REBUILD, "wheel");
watchPython("examples", PREVIEWS, "previews");

const next = spawn("next dev --port 6817", { stdio: "inherit", shell: true });
next.on("exit", (code) => process.exit(code ?? 1));
