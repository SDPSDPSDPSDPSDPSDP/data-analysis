// The only entry point to Python. One worker per browser tab, created on first
// use and kept across client-side navigation, so Pyodide loads once per visit.

// images are SVG markup.
export type RunResult = { images: string[]; stdout: string; error?: string };

// The worker runs code serially, so one endless run would block every later one.
const RUN_TIMEOUT_MS = 30_000;

let worker: Worker | undefined;
let ready: Promise<void> | undefined;
let nextId = 0;
const pending = new Map<number, (result: RunResult) => void>();
let watchdog: ReturnType<typeof setTimeout> | undefined;

/** Kills the worker and fails every queued run; the next run starts a fresh worker. */
function restart(error: string) {
  worker?.terminate();
  worker = ready = undefined;
  stopWatchdog();
  pending.forEach((resolveRun) => resolveRun({ images: [], stdout: "", error }));
  pending.clear();
}

function stopWatchdog() {
  clearTimeout(watchdog);
  watchdog = undefined;
}

// Times the run at the head of the worker queue: restarted on every result.
function armWatchdog() {
  stopWatchdog();
  if (pending.size === 0) return;
  watchdog = setTimeout(
    () => restart(`Run stopped after ${RUN_TIMEOUT_MS / 1000} s. Python was restarted.`),
    RUN_TIMEOUT_MS,
  );
}

/** Starts loading Python in the background. Resolves when it is ready to run code. */
export function load(): Promise<void> {
  if (ready) return ready;
  const current = new Worker("/pyodide.worker.mjs", { type: "module" });
  worker = current;
  ready = new Promise((resolve, reject) => {
    current.onerror = (e) => {
      const error = `Python worker crashed: ${e.message}`;
      reject(new Error(error));
      if (worker === current) restart(error);
    };
    current.onmessage = (e) => {
      const msg = e.data;
      if (msg.type === "ready") {
        if (msg.error) reject(new Error(msg.error));
        else resolve();
      } else if (msg.type === "result") {
        const resolveRun = pending.get(msg.id);
        if (!resolveRun) return restart(`Result for unknown run id ${msg.id}. Python was restarted.`);
        resolveRun(msg);
        pending.delete(msg.id);
        armWatchdog();
      }
    };
  });
  return ready;
}

export function run(code: string): Promise<RunResult> {
  const loaded = load();
  const id = nextId++;
  return new Promise((resolve) => {
    pending.set(id, resolve);
    worker!.postMessage({ id, code });
    // Loading is not timed (first Pyodide download is slow); a load failure is reported in the run result.
    loaded.then(() => {
      if (watchdog === undefined) armWatchdog();
    }, () => {});
  });
}
