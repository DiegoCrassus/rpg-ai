import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";

const styles: Record<Variant, string> = {
  primary: "bg-brand-600 hover:bg-brand-700 text-white",
  secondary: "bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-600",
  danger: "bg-red-800 hover:bg-red-700 text-white",
  ghost: "bg-transparent hover:bg-slate-800 text-slate-300",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`rounded-md px-4 py-2 text-sm font-medium transition ${styles[variant]} ${className}`}
      {...props}
    />
  );
}
