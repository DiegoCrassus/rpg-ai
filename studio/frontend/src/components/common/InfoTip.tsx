import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";

const VIEWPORT_MARGIN = 8;
const Z_INDEX = 10000;

type InfoTipProps = {
  /** Accessible name for the trigger button */
  label: string;
  children: ReactNode;
  /** Optional test id for E2E */
  testId?: string;
  /** Stop click from bubbling (e.g. inside timeline row buttons) */
  stopPropagation?: boolean;
  /** Popover width class */
  panelClassName?: string;
};

function clampPosition(
  trigger: DOMRect,
  panelWidth: number,
  panelHeight: number,
): { top: number; left: number } {
  const maxLeft = window.innerWidth - panelWidth - VIEWPORT_MARGIN;
  const maxTop = window.innerHeight - panelHeight - VIEWPORT_MARGIN;

  let left = trigger.left;
  if (left + panelWidth > window.innerWidth - VIEWPORT_MARGIN) {
    left = trigger.right - panelWidth;
  }
  left = Math.max(VIEWPORT_MARGIN, Math.min(left, maxLeft));

  let top = trigger.bottom + 4;
  if (top + panelHeight > window.innerHeight - VIEWPORT_MARGIN) {
    top = trigger.top - panelHeight - 4;
  }
  top = Math.max(VIEWPORT_MARGIN, Math.min(top, maxTop));

  return { top, left };
}

export function InfoTip({
  label,
  children,
  testId,
  stopPropagation = false,
  panelClassName = "w-64",
}: InfoTipProps) {
  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const tooltipId = useId();

  useLayoutEffect(() => {
    if (!open || !buttonRef.current || !panelRef.current) return;

    const trigger = buttonRef.current.getBoundingClientRect();
    const panel = panelRef.current;
    setCoords(clampPosition(trigger, panel.offsetWidth, panel.offsetHeight));
  }, [open, children, panelClassName]);

  useEffect(() => {
    if (!open) return;

    const reposition = () => {
      if (!buttonRef.current || !panelRef.current) return;
      const trigger = buttonRef.current.getBoundingClientRect();
      const panel = panelRef.current;
      setCoords(clampPosition(trigger, panel.offsetWidth, panel.offsetHeight));
    };

    window.addEventListener("resize", reposition);
    window.addEventListener("scroll", reposition, true);
    return () => {
      window.removeEventListener("resize", reposition);
      window.removeEventListener("scroll", reposition, true);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (buttonRef.current?.contains(target)) return;
      if (panelRef.current?.contains(target)) return;
      setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  const toggle = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (stopPropagation) event.stopPropagation();
    setOpen((value) => !value);
  };

  const panel =
    open && typeof document !== "undefined"
      ? createPortal(
          <div
            id={tooltipId}
            ref={panelRef}
            role="tooltip"
            style={{
              position: "fixed",
              top: coords?.top ?? -9999,
              left: coords?.left ?? -9999,
              zIndex: Z_INDEX,
              visibility: coords ? "visible" : "hidden",
            }}
            className={[
              "rounded-lg border border-slate-700 bg-slate-900 p-3 text-left text-xs leading-relaxed text-slate-300 shadow-xl",
              panelClassName,
            ].join(" ")}
          >
            {children}
          </div>,
          document.body,
        )
      : null;

  return (
    <span className="inline-flex align-middle">
      <button
        ref={buttonRef}
        type="button"
        data-testid={testId}
        aria-label={label}
        aria-expanded={open}
        aria-describedby={open ? tooltipId : undefined}
        className="inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-slate-800 hover:text-studio-accent focus:outline-none focus:ring-1 focus:ring-studio-accent/60"
        onClick={toggle}
      >
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-3.5 w-3.5" aria-hidden>
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clipRule="evenodd"
          />
        </svg>
      </button>
      {panel}
    </span>
  );
}
