/** Split YAML frontmatter (Cursor agent/command files) from Markdown body. */
export function splitFrontmatter(content: string): {
  frontmatter: string | null;
  body: string;
} {
  if (!content.startsWith("---\n")) {
    return { frontmatter: null, body: content };
  }
  const end = content.indexOf("\n---\n", 4);
  if (end === -1) {
    return { frontmatter: null, body: content };
  }
  return {
    frontmatter: content.slice(4, end).trim(),
    body: content.slice(end + 5),
  };
}
