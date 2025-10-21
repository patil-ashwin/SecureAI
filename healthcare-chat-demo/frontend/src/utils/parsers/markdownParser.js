// src/utils/parsers/markdownParser.js
import React from 'react';

export const parseMarkdown = (text) => {
  if (!text || typeof text !== 'string') return text;

  const createEntityLink = (entityType, entityId, key) => {
    import { getApiUrl } from '@config/api';
    let href, style;
    
    if (entityType.toLowerCase() === 'pae') {
      href = getApiUrl(`/paeentity/${entityId.toLowerCase()}`);
      style = { 
        color: '#58a6ff', 
        backgroundColor: 'rgba(88, 166, 255, 0.1)',
        border: '1px solid rgba(88, 166, 255, 0.2)'
      };
    } else {
      href = getApiUrl(`/peentity/${entityId.toLowerCase()}`);
      style = { 
        color: '#ffa657', 
        backgroundColor: 'rgba(255, 166, 87, 0.1)',
        border: '1px solid rgba(255, 166, 87, 0.2)'
      };
    }
    
    return React.createElement('a', {
      key,
      href,
      target: '_blank',
      rel: 'noopener noreferrer',
      style: {
        ...style,
        textDecoration: 'none',
        fontWeight: '600',
        padding: '2px 6px',
        borderRadius: '4px',
        margin: '0 2px',
        fontSize: '0.9em'
      },
      onClick: (e) => {
        e.preventDefault();
        window.open(href, '_blank');
      }
    }, entityId);
  };

  const createRiskIndicator = (level, key) => {
    const colors = {
      LOW: '#238636',
      MEDIUM: '#fb8500', 
      HIGH: '#da3633',
      CRITICAL: '#a40e26'
    };
    const color = colors[level.toUpperCase()] || '#6e7681';
    
    return React.createElement('span', {
      key,
      style: {
        color,
        backgroundColor: `${color}20`,
        border: `1px solid ${color}40`,
        fontWeight: '600',
        padding: '2px 6px',
        borderRadius: '4px',
        fontSize: '0.85em',
        textTransform: 'uppercase',
        margin: '0 2px'
      }
    }, level);
  };

  const processText = (text) => {
    const parts = [];
    let remaining = text;
    let key = 0;

    while (remaining.length > 0 && key < 100) {
      let found = false;

      // Risk indicators
      const riskMatch = remaining.match(/\{(LOW|MEDIUM|HIGH|CRITICAL)\}/i);
      if (riskMatch?.index !== undefined) {
        if (riskMatch.index > 0) {
          parts.push(remaining.substring(0, riskMatch.index));
        }
        parts.push(createRiskIndicator(riskMatch[1], `risk-${key++}`));
        remaining = remaining.substring(riskMatch.index + riskMatch[0].length);
        found = true;
        continue;
      }

      // Entity links
      const entityMatch = remaining.match(/\b(([Pp][Aa][Ee])|([Pp][Ee]))(\d+[\w\d]*)\b/);
      if (entityMatch?.index !== undefined) {
        if (entityMatch.index > 0) {
          parts.push(remaining.substring(0, entityMatch.index));
        }
        const entityType = entityMatch[2] ? 'pae' : 'pe';
        const entityId = entityMatch[1] + entityMatch[4];
        parts.push(createEntityLink(entityType, entityId, `entity-${key++}`));
        remaining = remaining.substring(entityMatch.index + entityMatch[0].length);
        found = true;
        continue;
      }

      // Bold text
      const boldMatch = remaining.match(/\*\*([^*]+)\*\*/);
      if (boldMatch?.index !== undefined) {
        if (boldMatch.index > 0) {
          parts.push(remaining.substring(0, boldMatch.index));
        }
        const content = boldMatch[1];
        if (content === 'HOTLISTED' || content === 'NOT HOTLISTED') {
          const isHotlisted = content === 'HOTLISTED';
          parts.push(React.createElement('span', {
            key: `hotlist-${key++}`,
            style: {
              color: isHotlisted ? '#f85149' : '#238636',
              backgroundColor: isHotlisted ? 'rgba(248, 81, 73, 0.1)' : 'rgba(35, 134, 54, 0.1)',
              border: `1px solid ${isHotlisted ? 'rgba(248, 81, 73, 0.3)' : 'rgba(35, 134, 54, 0.3)'}`,
              fontWeight: '700',
              padding: '3px 8px',
              borderRadius: '4px',
              textTransform: 'uppercase',
              fontSize: '0.85em'
            }
          }, content));
        } else {
          parts.push(React.createElement('strong', { 
            key: `bold-${key++}`,
            style: { fontWeight: '600', color: '#f0f6fc' }
          }, content));
        }
        remaining = remaining.substring(boldMatch.index + boldMatch[0].length);
        found = true;
        continue;
      }

      // Italic text
      const italicMatch = remaining.match(/\*([^*\n]+?)\*/);
      if (italicMatch?.index !== undefined) {
        if (italicMatch.index > 0) {
          parts.push(remaining.substring(0, italicMatch.index));
        }
        parts.push(React.createElement('em', { 
          key: `italic-${key++}`,
          style: { fontStyle: 'italic', color: '#8b949e' }
        }, italicMatch[1]));
        remaining = remaining.substring(italicMatch.index + italicMatch[0].length);
        found = true;
        continue;
      }

      // Code blocks
      const codeMatch = remaining.match(/`([^`\n]+?)`/);
      if (codeMatch?.index !== undefined) {
        if (codeMatch.index > 0) {
          parts.push(remaining.substring(0, codeMatch.index));
        }
        parts.push(React.createElement('code', {
          key: `code-${key++}`,
          style: {
            backgroundColor: '#21262d',
            color: '#79c0ff',
            padding: '2px 4px',
            borderRadius: '4px',
            fontSize: '0.9em',
            fontFamily: '"SF Mono", Monaco, Inconsolata, "Roboto Mono", Consolas, "Courier New", monospace'
          }
        }, codeMatch[1]));
        remaining = remaining.substring(codeMatch.index + codeMatch[0].length);
        found = true;
        continue;
      }

      if (!found) {
        parts.push(remaining);
        break;
      }
    }

    return parts.length > 1 ? parts : text;
  };

  // Split by lines and process each
  const lines = text.split('\n');
  const elements = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (!line) {
      elements.push(React.createElement('br', { key: `br-${i}` }));
      continue;
    }

    // Headers
    if (line.startsWith('#')) {
      const level = line.match(/^#+/)[0].length;
      const content = line.substring(level).trim();
      const Tag = `h${Math.min(level, 6)}`;
      elements.push(React.createElement(Tag, {
        key: `h-${i}`,
        style: { 
          fontWeight: '600', 
          margin: '16px 0 8px 0',
          color: '#f0f6fc',
          fontSize: level === 1 ? '1.5rem' : level === 2 ? '1.25rem' : '1.125rem'
        }
      }, processText(content)));
      continue;
    }

    // Lists
    if (line.match(/^[-*+]\s/)) {
      const content = line.substring(2);
      elements.push(React.createElement('div', {
        key: `list-${i}`,
        style: { 
          margin: '4px 0', 
          paddingLeft: '20px', 
          position: 'relative',
          color: '#f0f6fc'
        }
      }, [
        React.createElement('span', {
          key: 'bullet',
          style: { 
            position: 'absolute', 
            left: '8px', 
            color: '#58a6ff' 
          }
        }, '•'),
        processText(content)
      ]));
      continue;
    }

    // Regular paragraphs
    elements.push(React.createElement('p', {
      key: `p-${i}`,
      style: { 
        margin: '8px 0', 
        lineHeight: '1.6',
        color: '#f0f6fc'
      }
    }, processText(line)));
  }

  return React.createElement('div', {
    style: { 
      lineHeight: '1.6',
      fontSize: '15px',
      fontFamily: '"Söhne", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
    }
  }, elements);
};
