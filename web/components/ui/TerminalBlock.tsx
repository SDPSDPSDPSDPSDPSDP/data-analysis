"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import TerminalWindow from "@/components/ui/TerminalWindow";
import { charsPerStep, marker, parse, schedule, streamSteps } from "@/lib/terminalTranscript";
import { useVisible } from "@/lib/useVisible";

// Start only once the terminal is on screen, not ahead of it, so the stream is seen from its start.
const ON_SCREEN_MARGIN = "0px";

type Props = {
  transcript: string;
  // Image shown at the transcript's "[chart]" line.
  chart: string | null;
};

export default function TerminalBlock({ transcript, chart }: Props) {
  const lines = useMemo(() => parse(transcript), [transcript]);
  const { delays, starts } = useMemo(() => schedule(lines), [lines]);
  const hasChartLine = lines.some((line) => line.kind === "chart");
  if (hasChartLine && !chart) throw new Error("Transcript has a [chart] line but no chart");
  const root = useRef<HTMLDivElement>(null);
  const visible = useVisible(root, ON_SCREEN_MARGIN);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!visible || step >= delays.length) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setStep(delays.length);
      return;
    }
    const timer = setTimeout(() => setStep(step + 1), delays[step]);
    return () => clearTimeout(timer);
  }, [visible, step, delays]);

  const done = step >= delays.length;
  return (
    <TerminalWindow ref={root} role="img" aria-label={`Claude Code session:\n${transcript}`}>
      {/* Every line is rendered from the start, unrevealed ones hidden, so the terminal never changes height. */}
      <div className="terminal-body" aria-hidden>
        {lines.map((line, i) => {
          const shown = step - starts[i];
          const pending = shown <= 0 ? " terminal-pending" : "";
          if (line.kind === "gap") return <div key={i} className="terminal-gap" />;
          if (line.kind === "chart")
            return (
              <div key={i} className={`terminal-chart${pending}`}>
                <img src={chart!} alt="" />
              </div>
            );
          // The cursor stays at the end of a streamed line until the next line appears.
          const chars = charsPerStep(line);
          const revealed = chars ? Math.max(shown, 0) * chars : 0;
          const typing = chars !== undefined && !done && shown > 0 && shown <= streamSteps(line, chars);
          const text = chars ? (
            <>
              {line.text.slice(0, revealed)}
              {typing && <span className="terminal-cursor" />}
              <span className="terminal-unrevealed">{line.text.slice(revealed)}</span>
            </>
          ) : (
            line.text
          );
          return (
            <div key={i} className={`terminal-line terminal-${line.kind}${pending}`}>
              <span className="terminal-marker">{marker(line)}</span>
              {text}
            </div>
          );
        })}
      </div>
    </TerminalWindow>
  );
}
