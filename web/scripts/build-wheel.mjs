// Builds the shirin wheel from the repo root and copies it to public/shirin.whl,
// where the Pyodide worker fetches it.
import { execSync } from "node:child_process";
import { copyFileSync, mkdtempSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const outDir = mkdtempSync(join(tmpdir(), "shirin-wheel-"));
execSync(`uv build --wheel --out-dir "${outDir}"`, { cwd: "..", stdio: "inherit" });
const wheel = readdirSync(outDir).find((f) => f.endsWith(".whl"));
copyFileSync(join(outDir, wheel), join("public", "shirin.whl"));
console.log(`copied ${wheel} to public/shirin.whl`);
