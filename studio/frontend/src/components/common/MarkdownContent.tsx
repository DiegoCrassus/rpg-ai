import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { splitFrontmatter } from "./markdownUtils";

function mdComponents(compact: boolean): Components {
  return {
  h1: ({ children }) => (
    <h1
      className={[
        "border-b border-slate-700 font-bold text-white first:mt-0",
        compact ? "mb-2 mt-3 pb-1.5 text-lg" : "mb-3 mt-5 pb-2 text-xl",
      ].join(" ")}
    >
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2
      className={[
        "font-semibold text-white",
        compact ? "mb-1.5 mt-2.5 text-base" : "mb-2 mt-4 text-lg",
      ].join(" ")}
    >
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3
      className={[
        "font-semibold text-slate-100",
        compact ? "mb-1 mt-2 text-sm" : "mb-2 mt-3 text-base",
      ].join(" ")}
    >
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p className={[compact ? "mb-2 leading-snug" : "mb-3 leading-relaxed", "text-slate-300"].join(" ")}>
      {children}
    </p>
  ),
  ul: ({ children }) => (
    <ul
      className={[
        "list-disc pl-5 text-slate-300",
        compact ? "mb-2 space-y-0.5" : "mb-3 space-y-1",
      ].join(" ")}
    >
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol
      className={[
        "list-decimal pl-5 text-slate-300",
        compact ? "mb-2 space-y-0.5" : "mb-3 space-y-1",
      ].join(" ")}
    >
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="mb-3 border-l-2 border-studio-accent/50 pl-3 text-slate-400 italic">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      className="text-studio-accent underline decoration-studio-accent/40 hover:decoration-studio-accent"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  hr: () => <hr className={compact ? "my-2 border-slate-700" : "my-4 border-slate-700"} />,
  table: ({ children }) => (
    <div className="mb-3 overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm text-slate-300">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="border-b border-slate-600 text-slate-200">{children}</thead>,
  th: ({ children }) => <th className="px-2 py-1.5 font-medium">{children}</th>,
  td: ({ children }) => <td className="border-t border-slate-800 px-2 py-1.5">{children}</td>,
  code: ({ className, children }) => {
    const isInline = !className;
    if (isInline) {
      return (
        <code className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-xs text-sky-200">
          {children}
        </code>
      );
    }
    return (
      <code className={`font-mono text-xs leading-relaxed text-slate-200 ${className ?? ""}`}>
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre
      className={[
        "overflow-x-auto rounded-lg border border-slate-700 bg-slate-950",
        compact ? "mb-2 p-2" : "mb-3 p-3",
      ].join(" ")}
    >
      {children}
    </pre>
  ),
  strong: ({ children }) => <strong className="font-semibold text-slate-100">{children}</strong>,
  em: ({ children }) => <em className="text-slate-300">{children}</em>,
  };
}

type MarkdownContentProps = {
  source: string;
  /** Show YAML frontmatter block above rendered body */
  showFrontmatter?: boolean;
  /** Tighter spacing for constrained preview panes */
  compact?: boolean;
  className?: string;
  testId?: string;
};

export function MarkdownContent({
  source,
  showFrontmatter = true,
  compact = false,
  className = "",
  testId,
}: MarkdownContentProps) {
  const { frontmatter, body } = splitFrontmatter(source);
  const markdown = body.trim() || (frontmatter ? "" : source);

  return (
    <article
      data-testid={testId ?? "markdown-content"}
      className={["text-sm", className].filter(Boolean).join(" ")}
    >
      {showFrontmatter && frontmatter ? (
        <div
          className={[
            "rounded-lg border border-slate-700 bg-slate-900/80",
            compact ? "mb-2 p-2" : "mb-4 p-3",
          ].join(" ")}
        >
          <p className="mb-1 text-[10px] uppercase tracking-wide text-slate-500">Frontmatter</p>
          <pre className="overflow-x-hidden whitespace-pre-wrap break-words font-mono text-xs leading-snug text-slate-400">
            {frontmatter}
          </pre>
        </div>
      ) : null}
      {markdown ? (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents(compact)}>
          {markdown}
        </ReactMarkdown>
      ) : (
        <p className="text-slate-500">No Markdown body after frontmatter.</p>
      )}
    </article>
  );
}
