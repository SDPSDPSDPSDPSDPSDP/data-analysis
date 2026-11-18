import type { ComponentProps } from "react";

type Props = Omit<ComponentProps<"button">, "type" | "aria-label"> & { "aria-label": string };

export default function IconButton({ className, ...props }: Props) {
  return <button {...props} type="button" className={className ? `icon-button ${className}` : "icon-button"} />;
}
