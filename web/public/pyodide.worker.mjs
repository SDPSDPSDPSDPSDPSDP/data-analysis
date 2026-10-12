// Runs Python in a module worker. Lives in public/ instead of being bundled because
// Turbopack turns bundled workers into classic workers, which Pyodide refuses.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

// Replaces shirin's notebook display so every chart call appends its SVG to _out.
const SETUP = `
import shirin.plot.all_plots as _all_plots

_out = []
_all_plots.show = _out.append

import ast as _ast
from pyodide.code import CodeRunner as _CodeRunner

def _echo(value):
    if value is not None:
        print(value)

# Notebook-style: every top-level expression prints its value, so examples need no print().
# Fresh namespace per run: examples cannot leak state into each other or shadow _out.
async def _run(code):
    runner = _CodeRunner(code, return_mode="none")
    for node in runner.ast.body:
        if isinstance(node, _ast.Expr):
            call = _ast.Call(_ast.Name("_echo", _ast.Load()), [node.value], [])
            node.value = _ast.copy_location(call, node.value)
    _ast.fix_missing_locations(runner.ast)
    await runner.compile().run_async({"__name__": "__main__", "_echo": _echo})
`;

let stdout = [];

async function init() {
  const py = await loadPyodide();
  // Loading messages are not run output.
  await py.loadPackage(["micropip", "numpy", "pandas"], { messageCallback: () => {} });
  // micropip reads name and version from the filename, so give it a valid wheel name.
  // Revalidate so a rebuilt wheel is picked up without a hard reload.
  const response = await fetch("/shirin.whl", { cache: "no-cache" });
  if (!response.ok) throw new Error(`Fetching /shirin.whl failed: ${response.status} ${response.statusText}`);
  const wheel = await response.arrayBuffer();
  py.FS.writeFile("/tmp/shirin-0-py3-none-any.whl", new Uint8Array(wheel));
  await py.runPythonAsync(`import micropip; await micropip.install("emfs:/tmp/shirin-0-py3-none-any.whl")`);
  await py.runPythonAsync(SETUP);
  // Captured only from here on, so nothing printed while loading reaches a run's output.
  py.setStdout({ batched: (line) => stdout.push(line) });
  py.setStderr({ batched: (line) => stdout.push(line) });
  return py;
}

const ready = init();
ready.then(
  () => postMessage({ type: "ready" }),
  (err) => postMessage({ type: "ready", error: String(err) }),
);

// Runs share stdout and _out, so overlapping runs (StrictMode double effect) would
// steal each other's output. Serialize them.
let queue = Promise.resolve();
self.onmessage = (e) => {
  queue = queue.then(() => execute(e.data));
};

async function execute({ id, code }) {
  let py;
  try {
    py = await ready;
  } catch (err) {
    postMessage({ type: "result", id, images: [], stdout: "", error: `Python failed to load: ${err}` });
    return;
  }
  stdout = [];
  let error;
  try {
    py.globals.set("_code", code);
    await py.runPythonAsync("await _run(_code)");
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }
  const out = py.globals.get("_out");
  const images = out.toJs();
  out.clear();
  out.destroy();
  postMessage({ type: "result", id, images, stdout: stdout.join("\n"), error });
}
