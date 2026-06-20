import clsx from "clsx";
import { Priority, PRIORITY_LABELS, PRIORITY_COLOR_CLASS } from "@/lib/types";

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded px-2 py-1 text-xs font-semibold text-white font-mono",
        PRIORITY_COLOR_CLASS[priority]
      )}
    >
      P{priority} · {PRIORITY_LABELS[priority]}
    </span>
  );
}
