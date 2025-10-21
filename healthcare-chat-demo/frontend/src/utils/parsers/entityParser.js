// src/utils/parsers/entityParser.js
export const parseEntityReferences = (text) => {
  const entityRegex = /\b(PAE|PE)(\d+[\w\d]*)\b/gi;
  const matches = [];
  let match;
  
  while ((match = entityRegex.exec(text)) !== null) {
    matches.push({
      type: match[1].toLowerCase(),
      id: match[1] + match[2],
      startIndex: match.index,
      endIndex: match.index + match[0].length
    });
  }
  
  return matches;
};