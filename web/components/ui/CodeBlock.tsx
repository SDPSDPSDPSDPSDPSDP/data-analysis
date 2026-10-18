"use client";

import { useMemo, useRef, type RefObject } from "react";
import CodeMirror, { EditorSelection, keymap, Prec, type Extension } from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { oneDarkTheme } from "@codemirror/theme-one-dark";
import { tags } from "@lezer/highlight";
import CopyButton from "@/components/ui/CopyButton";
import { colorSwatches } from "@/components/ui/colorSwatches";
import { useDarkMode } from "@/lib/darkMode";

// oneDark editor chrome in dark mode, default chrome in light; syntax colors come from --code-* tokens in globals.css.
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

const lightTheme = syntaxHighlighting(highlightStyle);
const darkTheme = [oneDarkTheme, lightTheme];

// Python's smart indent re-aligns inside parens; users expect Enter to copy the line's own indent.
const keepIndentOnEnter = Prec.high(
  keymap.of([
    {
      key: "Enter",
      run: ({ state, dispatch }) => {
        const changes = state.changeByRange((range) => {
          const insert = "\n" + /^\s*/.exec(state.doc.lineAt(range.from).text)![0];
          return {
            changes: { from: range.from, to: range.to, insert },
            range: EditorSelection.cursor(range.from + insert.length),
          };
        });
        dispatch(state.update(changes, { scrollIntoView: true, userEvent: "input" }));
        return true;
      },
    },
  ]),
);

const NO_EXTENSIONS: Extension[] = [];

function runKey(onRun: RefObject<((value: string) => void) | undefined>) {
  return Prec.highest(keymap.of([{ key: "Mod-Enter", run: (view) => (onRun.current!(view.state.doc.toString()), true) }]));
}

type Props = {
  value: string;
  onChange?: (value: string) => void;
  // Called with the editor's code on Mod-Enter.
  onRun?: (value: string) => void;
  extensions?: Extension[];
};

// Read-only unless onChange is given.
export default function CodeBlock({ value, onChange, onRun, extensions = NO_EXTENSIONS }: Props) {
  // Callbacks change every render; a ref keeps the extension list stable so CodeMirror is not reconfigured per keystroke.
  const onRunRef = useRef(onRun);
  onRunRef.current = onRun;
  const dark = useDarkMode();
  const editable = Boolean(onChange);
  const runnable = Boolean(onRun);
  const allExtensions = useMemo(
    () => [
      python(),
      ...(editable ? [colorSwatches, keepIndentOnEnter] : []),
      ...(runnable ? [runKey(onRunRef)] : []),
      ...extensions,
    ],
    [editable, runnable, extensions],
  );
  return (
    <div className="code-block copyable">
      <CodeMirror
        value={value}
        onChange={onChange}
        editable={editable}
        readOnly={!editable}
        theme={dark ? darkTheme : lightTheme}
        extensions={allExtensions}
        height="100%"
      />
      <CopyButton copy={() => navigator.clipboard.writeText(value)} />
    </div>
  );
}
