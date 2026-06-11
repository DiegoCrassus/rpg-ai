type BuilderToastProps = {
  message: string | null;
  onDismiss: () => void;
};

export function BuilderToast({ message, onDismiss }: BuilderToastProps) {
  if (!message) {
    return null;
  }

  return (
    <div
      role="status"
      data-testid="builder-toast"
      className="fixed bottom-6 left-1/2 z-50 flex max-w-md -translate-x-1/2 items-center gap-3 rounded-lg border border-amber-500/40 bg-amber-950/90 px-4 py-3 text-sm text-amber-100 shadow-lg"
    >
      <span className="flex-1">{message}</span>
      <button
        type="button"
        onClick={onDismiss}
        className="rounded px-2 py-0.5 text-xs text-amber-200/80 hover:bg-amber-900/60 hover:text-white"
        aria-label="Dismiss"
      >
        Dismiss
      </button>
    </div>
  );
}
