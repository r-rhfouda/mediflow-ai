import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
}

const VARIANT_CLASSES: Record<string, string> = {
  primary: "bg-brand text-white hover:bg-brand-deep",
  secondary: "bg-white text-ink border border-line hover:border-brand",
  ghost: "bg-transparent text-ink hover:bg-brand-light",
  danger: "bg-priority-urgence text-white hover:opacity-90",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", className, ...props }, ref) => (
    <button
      ref={ref}
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded px-4 py-2 text-sm font-medium font-body transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
        VARIANT_CLASSES[variant],
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";
