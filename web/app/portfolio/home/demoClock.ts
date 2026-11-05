// Frame clock for the scripted demo: aborts with the signal, and time spent paused does not count,
// so a reader taking over never skips a step.
export function createDemoClock(signal: AbortSignal) {
  const clock = {
    paused: false,
    frame: () =>
      new Promise<void>((resolve, reject) => {
        if (signal.aborted) return reject(signal.reason);
        requestAnimationFrame(() => resolve());
      }),
    async wait(ms: number, onFrame?: (progress: number) => void) {
      let elapsed = 0;
      let last = performance.now();
      while (elapsed < ms) {
        await clock.frame();
        const now = performance.now();
        if (!clock.paused) elapsed += now - last;
        last = now;
        onFrame?.(Math.min(1, elapsed / ms));
      }
    },
  };
  return clock;
}
