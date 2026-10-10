"use client";

import CodeMirror, { type Extension } from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import CopyButton from "@/components/ui/CopyButton";

type Props = {
  value: string;
  onChange?: (value: string) => void;
  extensions?: Extension[];
};

// Read-only unless onChange is given.
export default function CodeBlock({ value, onChange, extensions = [] }: Props) {
  return (
    <div className="code-block copyable">
      <CodeMirror
        value={value}
        onChange={onChange}
        editable={Boolean(onChange)}
        readOnly={!onChange}
        theme="dark"
        extensions={[python(), ...extensions]}
        height="100%"
      />
      <CopyButton copy={() => navigator.clipboard.writeText(value)} />
    </div>
  );
}
