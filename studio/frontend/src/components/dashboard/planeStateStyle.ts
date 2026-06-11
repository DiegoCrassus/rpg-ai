export function planeStateGroupClass(group?: string): string {
  switch (group) {
    case "completed":
      return "border-emerald-500/40 bg-emerald-500/10 text-emerald-200";
    case "started":
      return "border-sky-500/40 bg-sky-500/10 text-sky-200";
    case "cancelled":
      return "border-red-500/40 bg-red-500/10 text-red-200";
    default:
      return "border-slate-600 bg-slate-800/80 text-slate-300";
  }
}
