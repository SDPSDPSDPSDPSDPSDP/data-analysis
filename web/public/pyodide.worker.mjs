// Runs Python in a module worker. Lives in public/ instead of being bundled because
// Turbopack turns bundled workers into classic workers, which Pyodide refuses.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

// Replaces plt.show so every call saves the current figure as a PNG, then
// renders one throwaway figure so matplotlib's font cache is built before the first run.
const SETUP = `
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, io, base64
from shirin.plot.config.matplotlib import build_rc

_out = []

def _show(*args, **kwargs):
    buf = io.BytesIO()
    plt.gcf().savefig(buf, format="png", dpi=200, bbox_inches="tight")
    _out.append(base64.b64encode(buf.getvalue()).decode())

plt.show = _show
build_rc(font="satoshi")
plt.figure().savefig(io.BytesIO())
plt.close("all")
`;

let stdout = [];

async function init() {
  const py = await loadPyodide();
  py.setStdout({ batched: (line) => stdout.push(line) });
  py.setStderr({ batched: (line) => stdout.push(line) });
  await py.loadPackage(["micropip", "matplotlib", "numpy", "pandas"]);
  // micropip reads name and version from the filename, so give it a valid wheel name.
  const wheel = await fetch("/shirin.whl").then((r) => r.arrayBuffer());
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
  py.runPython("_out.clear(); plt.close('all')");
  postMessage({ type: "result", id, images, stdout: stdout.join("\n"), error });
}
