import type { ComponentProps } from "react";

// Dark Claude Code window chrome: title bar with three dots, content below.
export default function TerminalWindow({ className, children, ...props }: ComponentProps<"div">) {
  return (
    <div {...props} className={className ? `terminal ${className}` : "terminal"}>
      <div className="terminal-bar" aria-hidden>
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-dot" />
        <span className="terminal-title">claude</span>
      </div>
      {children}
    </div>
  );
}
