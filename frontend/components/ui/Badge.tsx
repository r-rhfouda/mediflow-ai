import { HTMLAttributes } from "react";
import clsx from "clsx";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "success" | "warning" | "danger";
}

const TONE_CLASSES: Record<string, string> = {
  neutral: "bg-line text-ink",
  success: "bg-brand-light text-brand-deep",
  warning: "bg-amber-100 text-amber-800",
  danger: "bg-red-100 text-priority-urgence",
};

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-medium font-mono",
        TONE_CLASSES[tone],
        className
      )}
      {...props}
    />
  );
}
