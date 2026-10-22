"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useVisible } from "@/lib/useVisible";

type Line = { kind: "prompt" | "tool" | "reply" | "result" | "chart" | "gap"; text: string; first?: boolean };

const TOOL_CALL = /^\w+\(/;

// Delay before each streaming step, in ms. Prompt and replies stream per character, other lines appear whole.
const TYPE_DELAY = 35;
const REPLY_CHAR_DELAY = 12;
const LINE_DELAY: Record<Line["kind"], number> = { prompt: 400, tool: 700, reply: 500, result: 250, chart: 900, gap: 0 };
const CODE_LINE_DELAY = 80;

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
    } else if (raw.startsWith("  ")) lines.push({ kind: "result", text: raw.slice(2), first: previous?.kind !== "result" });
    else throw new Error(`Terminal line must start with "> ", "* ", two spaces or be [chart]: ${raw}`);
  }
  return lines;
}

const streamsChars = (line: Line) => line.kind === "prompt" || line.kind === "reply";

// Delay of every step and the step each line starts at; a char-streamed line takes one step per character.
function schedule(lines: Line[]) {
  const delays: number[] = [];
  const starts = lines.map((line) => {
    const start = delays.length;
    const code = line.kind === "result" && !line.first;
    delays.push(code ? CODE_LINE_DELAY : LINE_DELAY[line.kind]);
    if (streamsChars(line)) {
      const charDelay = line.kind === "prompt" ? TYPE_DELAY : REPLY_CHAR_DELAY;
      for (let i = 1; i < line.text.length; i++) delays.push(charDelay);
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
  if (lines.some((line) => line.kind === "chart") && !chart) throw new Error("Transcript has a [chart] line but no chart");
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
    <div ref={root} className="terminal" role="img" aria-label={`Claude Code session:\n${transcript}`}>
      <div className="terminal-bar" aria-hidden>
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-title">claude</span>
      </div>
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
          const typing = streamsChars(line) && !done && shown > 0 && shown <= line.text.length;
          const text = streamsChars(line) ? (
            <>
              {line.text.slice(0, Math.max(shown, 0))}
              {typing && <span className="terminal-cursor" />}
              <span className="terminal-unrevealed">{line.text.slice(Math.max(shown, 0))}</span>
            </>
          ) : (
            line.text
          );
          const marker = line.kind === "prompt" ? ">" : line.kind === "result" ? (line.first ? "⎿" : "") : "●";
          return (
            <div key={i} className={`terminal-line terminal-${line.kind}${pending}`}>
              <span className="terminal-marker">{marker}</span>
              {text}
            </div>
          );
        })}
      </div>
    </div>
  );
}
