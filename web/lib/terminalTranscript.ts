export type Line = { kind: "prompt" | "tool" | "reply" | "result" | "chart" | "gap"; text: string; first?: boolean };

const TOOL_CALL = /^\w+\(/;

// Delay before each streaming step, in ms. The prompt types per character, replies stream in chunks of
// characters (faster than timers can tick per character), other lines appear whole.
const STREAM: Partial<Record<Line["kind"], { chars: number; delay: number }>> = {
  prompt: { chars: 1, delay: 35 },
  reply: { chars: 6, delay: 16 },
};
const LINE_DELAY: Record<Line["kind"], number> = { prompt: 400, tool: 350, reply: 250, result: 150, chart: 400, gap: 0 };
const CODE_LINE_DELAY = 40;

// Transcript syntax: "> " user prompt, "* " Claude step (tool call when it reads Name(...)), indented lines its output,
// "[chart]" the chart.
export function parse(transcript: string): Line[] {
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

export const charsPerStep = (line: Line) => STREAM[line.kind]?.chars;
export const streamSteps = (line: Line, chars: number) => Math.ceil(line.text.length / chars);

export function marker(line: Line): string {
  if (line.kind === "prompt") return ">";
  if (line.kind === "result") return line.first ? "⎿" : "";
  return "●";
}

// Delay of every step and the step each line starts at; a streamed line takes one step per chunk of characters.
export function schedule(lines: Line[]) {
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
