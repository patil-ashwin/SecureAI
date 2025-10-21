import { getApiUrl } from '@config/api';
// frontend/src/utils/textFormatter.js

/**
 * Converts PAE/PE pattern text to clickable HTTP links
 * Clean professional styling without heavy borders
 */
const convertPAEPELinksToClickable = (text) => {
  if (!text) return '';
  
  // STRICT pattern: PAE/PE followed by NUMBERS ONLY
  const paePattern = /\b([Pp][Aa][Ee]|[Pp][Ee])(\d+)\b/g;
  
  return text.replace(paePattern, (match, prefix, numbers) => {
    const fullEntity = prefix + numbers;
    const entityType = prefix.toLowerCase().includes('pae') ? 'pae' : 'pe';
    const url = getApiUrl(`/${entityType}entity/${fullEntity.toLowerCase()}`);
    
    // Clean professional styling - subtle highlight without heavy borders
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color: #58a6ff; background-color: rgba(88, 166, 255, 0.08); text-decoration: none; font-weight: 500; padding: 1px 3px; border-radius: 3px; margin: 0 1px; font-size: 0.95em; transition: all 0.2s ease;" onmouseover="this.style.backgroundColor='rgba(88, 166, 255, 0.15)'" onmouseout="this.style.backgroundColor='rgba(88, 166, 255, 0.08)'">${match}</a>`;
  });
};

/**
 * Style account numbers and IDs for better readability
 */
const styleAccountNumbers = (text) => {
  if (!text) return '';
  
  // Pattern for account numbers (long numeric sequences)
  const accountPattern = /\b(\d{10,})\b/g;
  
  return text.replace(accountPattern, (match) => {
    // Professional styling for account numbers
    return `<span style="font-family: 'SF Mono', Monaco, 'Roboto Mono', monospace; background-color: #1a1a1a; color: #7dd3fc; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; border: 1px solid #2d2d2d; font-weight: 500;">${match}</span>`;
  });
};

/**
 * Style email addresses
 */
const styleEmailAddresses = (text) => {
  if (!text) return '';
  
  // Pattern for email addresses
  const emailPattern = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
  
  return text.replace(emailPattern, (match) => {
    // Professional styling for emails
    return `<span style="color: #a78bfa; background-color: rgba(167, 139, 250, 0.08); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; font-weight: 500;">${match}</span>`;
  });
};

/**
 * Style type indicators (like "PEEntity", "Email", "Account", etc.)
 */
const styleTypeIndicators = (text) => {
  if (!text) return '';
  
  // Pattern for type indicators that appear after "Type:"
  const typePattern = /(\bType:\s*)`([^`]+)`/g;
  
  return text.replace(typePattern, (match, prefix, type) => {
    // Professional badge styling for types
    return `${prefix}<span style="background: linear-gradient(135deg, #10a37f 0%, #0891b2 100%); color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">${type}</span>`;
  });
};

/**
 * Style section headers better - Updated to handle various formats
 */
const styleSectionHeaders = (text) => {
  if (!text) return '';
  
  // Handle markdown headers first (##, ###, etc.)
  let styled = text
    .replace(/^#{3}\s*([^#\n]*)/gm, '<h3 style="color: #e5e5e5; font-weight: 600; font-size: 16px; margin: 16px 0 8px 0; padding-bottom: 4px; border-bottom: 1px solid #333;">$1</h3>')
    .replace(/^#{2}\s*([^#\n]*)/gm, '<h2 style="color: #10a37f; font-weight: 700; font-size: 18px; margin: 20px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #10a37f;">$1</h2>')
    .replace(/^#{1}\s*([^#\n]*)/gm, '<h1 style="color: #10a37f; font-weight: 700; font-size: 20px; margin: 24px 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #10a37f;">$1</h1>');
  
  // Handle lettered sections like "g. AllAccounts", "h. Addresses"
  styled = styled.replace(/^([a-z])\.\s*([A-Za-z][^:\n]*)/gm, 
    '<div style="margin: 20px 0 12px 0; padding: 8px 0; border-bottom: 2px solid #333;"><span style="color: #10a37f; font-weight: 700; font-size: 16px; margin-right: 8px;">$1.</span><span style="color: #e5e5e5; font-weight: 600; font-size: 16px;">$2</span></div>'
  );
  
  return styled;
};

/**
 * Converts markdown tables to HTML tables with improved detection
 */
const convertMarkdownTablesToHTML = (text) => {
  if (!text) return '';
  
  const lines = text.split('\n');
  let result = [];
  let i = 0;
  
  while (i < lines.length) {
    const line = lines[i].trim();
    
    // Check if this line looks like a table row
    if (line.startsWith('|') && line.endsWith('|') && line.split('|').length > 2) {
      // Look ahead to see if next line is a separator or another table row
      const nextLine = lines[i + 1] ? lines[i + 1].trim() : '';
      
      // Check if we have a table header followed by separator
      if (nextLine.match(/^\|[\s\-:\|]+\|$/)) {
        // Found a proper table with header and separator
        const tableStart = i;
        let tableEnd = i + 1; // Include separator
        
        // Find all subsequent table rows
        for (let j = i + 2; j < lines.length; j++) {
          const tableLine = lines[j].trim();
          if (tableLine.startsWith('|') && tableLine.endsWith('|') && tableLine.split('|').length > 2) {
            tableEnd = j;
          } else if (tableLine === '') {
            // Allow empty lines within table
            continue;
          } else {
            // Not a table row anymore
            break;
          }
        }
        
        // Extract and convert table
        const tableLines = lines.slice(tableStart, tableEnd + 1).filter(line => {
          const trimmed = line.trim();
          return trimmed && !trimmed.match(/^\|[\s\-:\|]+\|$/); // Exclude separator lines
        });
        
        if (tableLines.length >= 1) { // At least header
          const htmlTable = convertTableLinesToHTML([tableLines[0], '|---|---|---|---|', ...tableLines.slice(1)]);
          result.push(htmlTable);
        }
        
        i = tableEnd + 1;
      } else if (nextLine.startsWith('|') && nextLine.endsWith('|')) {
        // Table without separator - collect all consecutive table rows
        const tableStart = i;
        let tableEnd = i;
        
        // Find all consecutive table rows
        for (let j = i; j < lines.length; j++) {
          const tableLine = lines[j].trim();
          if (tableLine.startsWith('|') && tableLine.endsWith('|') && tableLine.split('|').length > 2) {
            tableEnd = j;
          } else if (tableLine === '') {
            // Allow empty lines
            continue;
          } else {
            break;
          }
        }
        
        if (tableEnd > tableStart) {
          // We have multiple table rows - treat first as header
          const tableLines = lines.slice(tableStart, tableEnd + 1).filter(line => line.trim());
          const htmlTable = convertTableLinesToHTML([tableLines[0], '|---|---|---|---|', ...tableLines.slice(1)]);
          result.push(htmlTable);
          i = tableEnd + 1;
        } else {
          // Single table row - not a table
          result.push(line);
          i++;
        }
      } else {
        // Single table row - not a table
        result.push(line);
        i++;
      }
    } else {
      result.push(line);
      i++;
    }
  }
  
  return result.join('\n');
};

/**
 * Convert array of table lines to HTML table
 */
const convertTableLinesToHTML = (tableLines) => {
  if (tableLines.length < 3) return tableLines.join('\n');
  
  let html = '<table style="border-collapse: collapse; width: 100%; margin: 20px 0; background: linear-gradient(145deg, #1a1a1a 0%, #1e1e1e 100%); border: 1px solid #333; border-radius: 8px; overflow: hidden; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">';
  
  // Process header
  const headerCells = tableLines[0].split('|').map(cell => cell.trim()).filter(cell => cell !== '');
  html += '<thead><tr style="background: linear-gradient(135deg, #2a2a2a 0%, #333 100%);">';
  headerCells.forEach(cell => {
    html += `<th style="padding: 14px 12px; border-bottom: 2px solid #444; color: #fff; font-weight: 600; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">${cell}</th>`;
  });
  html += '</tr></thead><tbody>';
  
  // Process data rows
  for (let i = 2; i < tableLines.length; i++) {
    const cells = tableLines[i].split('|').map(cell => cell.trim()).filter(cell => cell !== '');
    html += '<tr style="border-bottom: 1px solid #2a2a2a; transition: background-color 0.2s ease;" onmouseover="this.style.backgroundColor=\'#242424\'" onmouseout="this.style.backgroundColor=\'transparent\'">';
    cells.forEach((cell, index) => {
      html += `<td style="padding: 12px; color: #d1d5db; border-right: ${index < cells.length - 1 ? '1px solid #2a2a2a' : 'none'}; font-size: 13px; line-height: 1.4;">${cell}</td>`;
    });
    html += '</tr>';
  }
  
  html += '</tbody></table>';
  return html;
};

export const formatAnalysisText = (text) => {
  if (!text) return '';
  
  // STEP 1: Handle markdown tables FIRST
  let formatted = convertMarkdownTablesToHTML(text);
  
  // STEP 2: Style section headers early (includes markdown headers)
  formatted = styleSectionHeaders(formatted);
  
  // STEP 3: Process other markdown formatting
  formatted = formatted
    // Convert **text** to <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color: #ffffff; font-weight: 600;">$1</strong>')
    
    // Remove standalone --- lines
    .replace(/^[\s]*---+[\s]*$/gm, '')
    
    // Style type indicators
    .replace(/(\bType:\s*)`([^`]+)`/g, '$1<span style="background: linear-gradient(135deg, #10a37f 0%, #0891b2 100%); color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">$2</span>')
    
    // Handle other backticks for code
    .replace(/`([^`]+)`/g, '<code style="background: #1a1a1a; color: #7dd3fc; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; border: 1px solid #2d2d2d; font-family: \'SF Mono\', Monaco, monospace;">$1</code>')
    
    // Fix bullet point formatting
    .replace(/- \*\*(.*?)\*\*:?-\s*/g, '\n\n<strong style="color: #ffffff;">$1:</strong>\n- ')
    .replace(/- \*\*(.*?)\*\*:?\s*\n/g, '\n\n<strong style="color: #ffffff;">$1:</strong>\n')
    
    // Fix nested bullet points
    .replace(/^[\s]*-[\s]*/gm, '\n• ')
    .replace(/^[\s]*\*[\s]*/gm, '\n• ')
    
    // Clean up excessive newlines
    .replace(/\n\s*\n\s*\n+/g, '\n\n')
    .replace(/^\s+|\s+$/g, '');
  
  // STEP 4: Handle paragraph wrapping
  formatted = formatted
    .split('\n\n')
    .map(paragraph => paragraph.replace(/\n/g, '<br>'))
    .join('\n\n')
    .split('\n\n')
    .map(section => {
      section = section.trim();
      if (!section) return '';
      // Skip already processed elements
      if (section.startsWith('<h1>') || section.startsWith('<h2>') || section.startsWith('<h3>') || 
          section.startsWith('<strong>') || section.startsWith('<table') || section.startsWith('<div')) {
        return section;
      }
      return `<p style="margin: 8px 0; line-height: 1.6; color: #d1d5db;">${section}</p>`;
    })
    .filter(section => section)
    .join('\n\n');

  // STEP 5: Apply styling enhancements as final steps
  formatted = styleAccountNumbers(formatted);
  formatted = styleEmailAddresses(formatted);
  formatted = convertPAEPELinksToClickable(formatted);
  
  return formatted;
};

export const extractRingId = (text) => {
  if (!text) return null;
  
  const patterns = [
    /ring\s+(\d+)/i,
    /Ring ID:\s*(\d+)/i,
    /export ring (\d+)/i,
    /analyze ring (\d+)/i,
    /ring (\d{3,})/i
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1];
  }
  
  return null;
};

export const isRingAnalysis = (text) => {
  if (!text) return false;
  
  const indicators = [
    'PAE Entities',
    'Ring Composition', 
    'Key Findings',
    'fraud ring',
    'Addresses:',
    'Zelle Tokens',
    'Email Addresses',
    'Recommendations',
    'Summary Table'
  ];
  
  return indicators.some(indicator => 
    text.toLowerCase().includes(indicator.toLowerCase())
  );
};

// Export functions
export { convertPAEPELinksToClickable, convertMarkdownTablesToHTML, styleAccountNumbers, styleEmailAddresses };