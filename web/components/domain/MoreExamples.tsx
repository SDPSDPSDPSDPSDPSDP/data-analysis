import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import SectionIcon from "@/components/domain/SectionIcon";

type Props = { title: string; count: number; expanded: boolean; children: ReactNode };

export default function MoreExamples({ title, count, expanded, children }: Props) {
  if (expanded) return <div className="more-examples">{children}</div>;
  return (
    <details className="more-examples">
      <summary>
        <span className="more-examples-button">
          <SectionIcon title={title} />
          <span className="more-examples-closed">{count} more examples</span>
          <span className="more-examples-open">Hide examples</span>
          <ChevronDown size="1em" className="more-examples-chevron" aria-hidden />
        </span>
      </summary>
      {children}
    </details>
  );
}
