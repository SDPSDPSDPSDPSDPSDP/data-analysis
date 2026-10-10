"use client";

import CodeMirror, { type Extension } from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import CopyButton from "@/components/ui/CopyButton";

type Props = {
  value: string;
  onChange?: (value: string) => void;
  extensions?: Extension[];
  className?: string;
};

// Read-only unless onChange is given.
export default function CodeBlock({ value, onChange, extensions = [], className = "" }: Props) {
  return (
    <div className={`code-block copyable ${className}`}>
      <CodeMirror
        value={value}
        onChange={onChange}
        editable={Boolean(onChange)}
        readOnly={!onChange}
        extensions={[python(), ...extensions]}
        height="100%"
      />
      <CopyButton copy={() => navigator.clipboard.writeText(value)} />
    </div>
  );
}
