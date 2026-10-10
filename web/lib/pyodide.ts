// The only entry point to Python. One worker per browser tab, created on first
// use and kept across client-side navigation, so Pyodide loads once per visit.

export type RunResult = { images: string[]; stdout: string; error?: string };

let worker: Worker | undefined;
let ready: Promise<void> | undefined;
let nextId = 0;
const pending = new Map<number, (result: RunResult) => void>();

/** Starts loading Python in the background. Resolves when it is ready to run code. */
export function load(): Promise<void> {
  if (ready) return ready;
  worker = new Worker("/pyodide.worker.mjs", { type: "module" });
  ready = new Promise((resolve, reject) => {
    worker!.onmessage = (e) => {
      const msg = e.data;
      if (msg.type === "ready") {
        if (msg.error) reject(new Error(msg.error));
        else resolve();
      } else if (msg.type === "result") {
        pending.get(msg.id)?.(msg);
        pending.delete(msg.id);
      }
    };
  });
  return ready;
}

export function run(code: string): Promise<RunResult> {
  load().catch(() => {}); // a load failure is reported in the run result
  const id = nextId++;
  return new Promise((resolve) => {
    pending.set(id, resolve);
    worker!.postMessage({ id, code });
  });
}
