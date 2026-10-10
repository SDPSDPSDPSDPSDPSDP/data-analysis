// Runs Python in a module worker. Lives in public/ instead of being bundled because
// Turbopack turns bundled workers into classic workers, which Pyodide refuses.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

// Replaces shirin's notebook display so every chart call appends its SVG to _out.
const SETUP = `
import shirin.plot.all_plots as _all_plots

_out = []
_all_plots.show = _out.append
`;

let stdout = [];

async function init() {
  const py = await loadPyodide();
  py.setStdout({ batched: (line) => stdout.push(line) });
  py.setStderr({ batched: (line) => stdout.push(line) });
  await py.loadPackage(["micropip", "numpy", "pandas"]);
  // micropip reads name and version from the filename, so give it a valid wheel name.
  // Revalidate so a rebuilt wheel is picked up without a hard reload.
  const wheel = await fetch("/shirin.whl", { cache: "no-cache" }).then((r) => r.arrayBuffer());
  py.FS.writeFile("/tmp/shirin-0-py3-none-any.whl", new Uint8Array(wheel));
  await py.runPythonAsync(`import micropip; await micropip.install("emfs:/tmp/shirin-0-py3-none-any.whl")`);
  await py.runPythonAsync(SETUP);
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
  stdout = [];
  let py;
  try {
    py = await ready;
  } catch (err) {
    postMessage({ type: "result", id, images: [], stdout: "", error: `Python failed to load: ${err}` });
    return;
  }
  let error;
  try {
    await py.runPythonAsync(code);
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }
  const images = py.runPython("_out[:]").toJs();
  py.runPython("_out.clear()");
  postMessage({ type: "result", id, images, stdout: stdout.join("\n"), error });
}
