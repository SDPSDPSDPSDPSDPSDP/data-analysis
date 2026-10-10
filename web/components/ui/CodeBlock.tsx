"use client";

import CodeMirror, { keymap, Prec, type Extension } from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { oneDarkTheme } from "@codemirror/theme-one-dark";
import { tags } from "@lezer/highlight";
import CopyButton from "@/components/ui/CopyButton";
import { colorSwatches } from "@/components/ui/colorSwatches";

// oneDark editor chrome, but syntax colors come from --code-* tokens in globals.css.
const highlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: "var(--code-keyword)" },
  { tag: [tags.name, tags.propertyName], color: "var(--code-name)" },
  { tag: [tags.function(tags.variableName), tags.labelName], color: "var(--code-function)" },
  {
    tag: [tags.constant(tags.name), tags.standard(tags.name), tags.atom, tags.bool, tags.special(tags.variableName)],
    color: "var(--code-constant)",
  },
  { tag: [tags.definition(tags.name), tags.separator, tags.punctuation], color: "var(--code-text)" },
  { tag: [tags.typeName, tags.className, tags.number, tags.self, tags.namespace], color: "var(--code-class)" },
  { tag: [tags.operator, tags.operatorKeyword, tags.escape, tags.special(tags.string)], color: "var(--code-operator)" },
  { tag: tags.string, color: "var(--code-string)" },
  { tag: [tags.meta, tags.comment], color: "var(--code-comment)" },
]);

const theme = [oneDarkTheme, syntaxHighlighting(highlightStyle)];

type Props = {
  value: string;
  onChange?: (value: string) => void;
  // Called with the editor's code on Mod-Enter.
  onRun?: (value: string) => void;
  extensions?: Extension[];
};

// Read-only unless onChange is given.
export default function CodeBlock({ value, onChange, onRun, extensions = [] }: Props) {
  const runKey = onRun
    ? [Prec.highest(keymap.of([{ key: "Mod-Enter", run: (view) => (onRun(view.state.doc.toString()), true) }]))]
    : [];
  return (
    <div className="code-block copyable">
      <CodeMirror
        value={value}
        onChange={onChange}
        editable={Boolean(onChange)}
        readOnly={!onChange}
        theme={theme}
        extensions={[python(), ...(onChange ? [colorSwatches] : []), ...runKey, ...extensions]}
        height="100%"
      />
      <CopyButton copy={() => navigator.clipboard.writeText(value)} />
    </div>
  );
}
