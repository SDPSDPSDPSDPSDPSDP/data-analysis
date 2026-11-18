import type { ComponentProps } from "react";

export default function LinkButton({ className, ...props }: Omit<ComponentProps<"button">, "type">) {
  return <button {...props} type="button" className={className ? `link-button ${className}` : "link-button"} />;
}
