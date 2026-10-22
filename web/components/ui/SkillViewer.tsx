"use client";

import { isValidElement, useRef, useState, type ReactElement, type ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import { EditorView } from "@uiw/react-codemirror";
import remarkGfm from "remark-gfm";
import { FileText, ScrollText } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import TerminalWindow from "@/components/ui/TerminalWindow";

// Module level: a new array per render would reconfigure every CodeMirror.
const WRAP_LINES = [EditorView.lineWrapping];

export type Skill = {
  name: string;
  // Frontmatter description: what Claude reads to decide when to load the skill.
  description: string;
  plugin: string;
  version: string;
  files: { name: string; content: string }[];
};

type Props = {
  skill: Skill;
};

export default function SkillViewer({ skill }: Props) {
  const [active, setActive] = useState(skill.files[0].name);
  const contentRef = useRef<HTMLDivElement>(null);
  const open = (name: string) => {
    setActive(name);
    contentRef.current!.scrollTop = 0;
  };
  const file = skill.files.find((f) => f.name === active)!;
  const components: Components = {
    // Fenced code reuses the site's code block; inline code stays a <code>.
    pre: ({ children }) => {
      const code = isValidElement(children) ? (children as ReactElement<{ children: ReactNode }>) : null;
      if (!code) throw new Error("Markdown <pre> without a <code> child");
      return <CodeBlock value={String(code.props.children).replace(/\n$/, "")} extensions={WRAP_LINES} />;
    },
    table: ({ children }) => <table className="data-table">{children}</table>,
    // Links to another file of the skill switch tabs, like Claude following them.
    a: ({ href, children }) =>
      skill.files.some((f) => f.name === href) ? (
        <button type="button" className="skill-link" onClick={() => open(href!)}>
          {children}
        </button>
      ) : (
        <a href={href} target="_blank" rel="noreferrer">
          {children}
        </a>
      ),
  };
  return (
    <TerminalWindow className="skill">
      <div className="skill-header">
        <span className="skill-icon">
          <ScrollText size="1em" aria-hidden />
        </span>
        <div>
          <div className="skill-name">{skill.name}</div>
          <div className="skill-meta">
            from {skill.plugin} plugin · v{skill.version}
          </div>
        </div>
      </div>
      <div className="skill-description">
        <p>{skill.description}</p>
      </div>
      <div className="skill-body">
        <nav className="skill-files" aria-label="Skill files">
          {skill.files.map((f) => (
            <button
              key={f.name}
              type="button"
              className="skill-file"
              aria-current={f.name === active}
              onClick={() => open(f.name)}
            >
              <FileText size="1em" aria-hidden />
              {f.name}
            </button>
          ))}
        </nav>
        <div className="skill-content" ref={contentRef}>
          <div className="skill-markdown">
            <Markdown remarkPlugins={[remarkGfm]} components={components}>
              {file.content}
            </Markdown>
          </div>
        </div>
      </div>
    </TerminalWindow>
  );
}
