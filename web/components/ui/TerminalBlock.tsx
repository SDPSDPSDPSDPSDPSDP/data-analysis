type Line = { kind: "prompt" | "tool" | "reply" | "result" | "gap"; text: string; first?: boolean };

const TOOL_CALL = /^\w+\(/;

// Transcript syntax: "> " user prompt, "* " Claude step (tool call when it reads Name(...)), indented lines its output.
function parse(transcript: string): Line[] {
  const lines: Line[] = [];
  for (const raw of transcript.split(/\r?\n/)) {
    const previous = lines[lines.length - 1];
    if (!raw.trim()) lines.push({ kind: "gap", text: "" });
    else if (raw.startsWith("> ")) lines.push({ kind: "prompt", text: raw.slice(2) });
    else if (raw.startsWith("* ")) {
      const text = raw.slice(2);
      lines.push({ kind: TOOL_CALL.test(text) ? "tool" : "reply", text });
    } else if (raw.startsWith("  ")) lines.push({ kind: "result", text: raw.slice(2), first: previous?.kind !== "result" });
    else throw new Error(`Terminal line must start with "> ", "* " or two spaces: ${raw}`);
  }
  return lines;
}

type Props = {
  transcript: string;
};

export default function TerminalBlock({ transcript }: Props) {
  return (
    <div className="terminal" role="img" aria-label={`Claude Code session:\n${transcript}`}>
      <div className="terminal-bar" aria-hidden>
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-title">claude</span>
      </div>
      <div className="terminal-body" aria-hidden>
        {parse(transcript).map((line, i) => {
          if (line.kind === "gap") return <div key={i} className="terminal-gap" />;
          if (line.kind === "prompt")
            return (
              <div key={i} className="terminal-line terminal-prompt">
                <span className="terminal-marker">&gt;</span>
                {line.text}
              </div>
            );
          if (line.kind === "result")
            return (
              <div key={i} className="terminal-line terminal-result">
                <span className="terminal-marker">{line.first ? "⎿" : ""}</span>
                {line.text}
              </div>
            );
          return (
            <div key={i} className={`terminal-line terminal-${line.kind}`}>
              <span className="terminal-marker">{"●"}</span>
              {line.text}
            </div>
          );
        })}
      </div>
    </div>
  );
}
