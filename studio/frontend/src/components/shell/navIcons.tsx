import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function base(props: IconProps) {
  return {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.75,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
    ...props,
  };
}

export function IconDashboard(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3" y="3" width="7" height="9" rx="1" />
      <rect x="14" y="3" width="7" height="5" rx="1" />
      <rect x="14" y="12" width="7" height="9" rx="1" />
      <rect x="3" y="16" width="7" height="5" rx="1" />
    </svg>
  );
}

export function IconWorkflows(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="12" cy="18" r="2.5" />
      <path d="M8 6h8M7 8l3 8M17 8l-3 8" />
    </svg>
  );
}

export function IconBuilder(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M14 4l6 6-9 9H5v-6z" />
      <path d="M13 5l6 6" />
    </svg>
  );
}

export function IconAgents(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c0-3.5 3.1-6 7-6s7 2.5 7 6" />
      <circle cx="18" cy="7" r="2" />
      <path d="M18 11c2 0 3.5 1.2 3.5 3" />
    </svg>
  );
}

export function IconRules(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M6 4h12v16H6z" />
      <path d="M9 8h6M9 12h6M9 16h4" />
    </svg>
  );
}

export function IconCommands(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M5 7l3 3-3 3" />
      <path d="M11 13h8" />
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  );
}

export function IconRegistry(props: IconProps) {
  return (
    <svg {...base(props)}>
      <ellipse cx="12" cy="6" rx="7" ry="3" />
      <path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6" />
      <path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" />
    </svg>
  );
}

export function IconValidation(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 3l8 4v5c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V7z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

export function IconSimulation(props: IconProps) {
  return (
    <svg {...base(props)}>
      <polygon points="8,5 19,12 8,19" fill="currentColor" stroke="none" />
      <rect x="4" y="5" width="2" height="14" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconAssistance(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 3a7 7 0 00-4 12.7V19h8v-3.3A7 7 0 0012 3z" />
      <path d="M10 22h4" />
    </svg>
  );
}

export function IconObservability(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M4 18V6M8 18V10M12 18V4M16 18v-6M20 18v-3" />
    </svg>
  );
}

export function IconEvidence(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M8 4h11v16H8z" />
      <path d="M8 8H5a1 1 0 00-1 1v10h4" />
      <path d="M11 9h5M11 13h5M11 17h3" />
    </svg>
  );
}

export function IconSettings(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

export function IconChevronLeft(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M14 6l-6 6 6 6" />
    </svg>
  );
}

export function IconChevronRight(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M10 6l6 6-6 6" />
    </svg>
  );
}
