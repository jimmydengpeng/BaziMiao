export const renderMarkdown = (text: string) => {
  if (!text) return '';

  const escape = (value: string) =>
    value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  const inline = (value: string) =>
    value
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>');

  const lines = escape(text).split(/\r?\n/);
  let html = '';
  let listType: 'ul' | 'ol' | null = null;

  const closeList = () => {
    if (listType) {
      html += `</${listType}>`;
      listType = null;
    }
  };

  const openList = (type: 'ul' | 'ol') => {
    if (listType && listType !== type) {
      closeList();
    }
    if (!listType) {
      listType = type;
      html += `<${type}>`;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      html += '<br>';
      continue;
    }

    const unorderedMatch = /^\s*[-*]\s+(.+)$/.exec(rawLine);
    if (unorderedMatch) {
      openList('ul');
      html += `<li>${inline(unorderedMatch[1].trim())}</li>`;
      continue;
    }

    const orderedMatch = /^\s*\d+\.\s+(.+)$/.exec(rawLine);
    if (orderedMatch) {
      openList('ol');
      html += `<li>${inline(orderedMatch[1].trim())}</li>`;
      continue;
    }

    const headingMatch = /^\s{0,3}(#{1,4})\s+(.+)$/.exec(rawLine);
    if (headingMatch) {
      closeList();
      const level = Math.min(4, headingMatch[1].length);
      html += `<h${level}>${inline(headingMatch[2].trim())}</h${level}>`;
      continue;
    }

    closeList();
    html += `<p>${inline(rawLine)}</p>`;
  }

  closeList();
  return html;
};

