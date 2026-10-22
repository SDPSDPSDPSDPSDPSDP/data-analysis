"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import TerminalWindow from "@/components/ui/TerminalWindow";
import { useVisible } from "@/lib/useVisible";

type Line = { kind: "prompt" | "tool" | "reply" | "result" | "chart" | "gap"; text: string; first?: boolean };

const TOOL_CALL = /^\w+\(/;

// Delay before each streaming step, in ms. The prompt types per character, replies stream in chunks of
// characters (faster than timers can tick per character), other lines appear whole.
const STREAM: Partial<Record<Line["kind"], { chars: number; delay: number }>> = {
  prompt: { chars: 1, delay: 35 },
  reply: { chars: 6, delay: 16 },
};
const LINE_DELAY: Record<Line["kind"], number> = { prompt: 400, tool: 350, reply: 250, result: 150, chart: 400, gap: 0 };
const CODE_LINE_DELAY = 40;

// Start only once the terminal is on screen, not ahead of it, so the stream is seen from its start.
const ON_SCREEN_MARGIN = "0px";

// Transcript syntax: "> " user prompt, "* " Claude step (tool call when it reads Name(...)), indented lines its output,
// "[chart]" the chart.
function parse(transcript: string): Line[] {
  const lines: Line[] = [];
  for (const raw of transcript.split(/\r?\n/)) {
    const previous = lines[lines.length - 1];
    if (!raw.trim()) lines.push({ kind: "gap", text: "" });
    else if (raw === "[chart]") lines.push({ kind: "chart", text: "" });
    else if (raw.startsWith("> ")) lines.push({ kind: "prompt", text: raw.slice(2) });
    else if (raw.startsWith("* ")) {
      const text = raw.slice(2);
      lines.push({ kind: TOOL_CALL.test(text) ? "tool" : "reply", text });
    } else if (raw.startsWith("  ")) {
      lines.push({ kind: "result", text: raw.slice(2), first: previous?.kind !== "result" });
    } else throw new Error(`Terminal line must start with "> ", "* ", two spaces or be [chart]: ${raw}`);
  }
  return lines;
}

const charsPerStep = (line: Line) => STREAM[line.kind]?.chars;
const streamSteps = (line: Line, chars: number) => Math.ceil(line.text.length / chars);

function marker(line: Line): string {
  if (line.kind === "prompt") return ">";
  if (line.kind === "result") return line.first ? "⎿" : "";
  return "●";
}

// Delay of every step and the step each line starts at; a streamed line takes one step per chunk of characters.
function schedule(lines: Line[]) {
  const delays: number[] = [];
  const starts = lines.map((line) => {
    const start = delays.length;
    const code = line.kind === "result" && !line.first;
    delays.push(code ? CODE_LINE_DELAY : LINE_DELAY[line.kind]);
    const stream = STREAM[line.kind];
    if (stream) {
      for (let i = 1; i < streamSteps(line, stream.chars); i++) delays.push(stream.delay);
    }
    return start;
  });
  return { delays, starts };
}

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
