/**
 * Utility functions to normalize and format AI output from different models
 * Handles various markdown formats, plain text, and edge cases
 */

/**
 * Normalize AI output to ensure consistent markdown formatting
 * @param {string} text - Raw AI output text
 * @returns {string} - Normalized markdown text
 */
export function normalizeAIOutput(text) {
  if (!text) return '';
  
  let normalized = text;
  
  // 1. Normalize line breaks (handle CRLF, LF, and multiple line breaks)
  normalized = normalized.replace(/\r\n/g, '\n');
  normalized = normalized.replace(/\r/g, '\n');
  
  // 2. Fix heading formats - ensure space after hash
  normalized = normalized.replace(/^(#{1,6})([^\s#])/gm, '$1 $2');
  
  // 3. Fix bold formatting - normalize **text** and __text__
  normalized = normalized.replace(/__([^_]+)__/g, '**$1**');
  
  // 4. Fix italic formatting - normalize *text* and _text_
  normalized = normalized.replace(/\b_([^_\s][^_]*[^_\s])_\b/g, '*$1*');
  
  // 5. Convert single-line code blocks to inline code
  // This fixes AI models that use code blocks for magnitude values
  normalized = normalized.replace(/```([^\n`]*?)```/g, '`$1`');
  normalized = normalized.replace(/^```\s*\n([^\n]+)\n```$/gm, '`$1`');
  
  // 6. Normalize list items - ensure consistent spacing
  normalized = normalized.replace(/^[\s]*[-*+]\s+/gm, '- ');
  normalized = normalized.replace(/^[\s]*(\d+)\.\s+/gm, '$1. ');
  
  // 7. Add blank line before headings if missing
  normalized = normalized.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2');
  
  // 8. Add blank line after headings if missing
  normalized = normalized.replace(/(#{1,6}\s[^\n]+)\n([^#\n])/g, '$1\n\n$2');
  
  // 9. Fix bullet points without proper markdown
  // Convert lines starting with • or · to markdown bullets
  normalized = normalized.replace(/^[\s]*[•·]\s+/gm, '- ');
  
  // 10. Normalize numbered lists - ensure they start from 1
  const lines = normalized.split('\n');
  let inNumberedList = false;
  let listCounter = 1;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const numberedListMatch = line.match(/^(\s*)(\d+)\.\s/);
    
    if (numberedListMatch) {
      if (!inNumberedList) {
        inNumberedList = true;
        listCounter = 1;
      }
      lines[i] = line.replace(/^\s*\d+\./, `${numberedListMatch[1]}${listCounter}.`);
      listCounter++;
    } else if (line.trim() !== '' && !line.match(/^\s*[-*]/)) {
      inNumberedList = false;
      listCounter = 1;
    }
  }
  normalized = lines.join('\n');
  
  // 10. Fix code blocks - ensure proper fencing
  normalized = normalized.replace(/```(\w*)\n/g, '```$1\n');
  normalized = normalized.replace(/\n```/g, '\n```\n');
  
  // 11. Remove excessive blank lines (more than 2 consecutive)
  normalized = normalized.replace(/\n{4,}/g, '\n\n\n');
  
  // 12. Fix inline code - ensure backticks are properly closed
  const backtickCount = (normalized.match(/`/g) || []).length;
  if (backtickCount % 2 !== 0) {
    // Odd number of backticks, add one at the end
    normalized += '`';
  }
  
  // 13. Handle blockquotes - normalize > formatting
  normalized = normalized.replace(/^>\s*/gm, '> ');
  
  // 14. Fix tables - ensure proper spacing
  normalized = normalized.replace(/\|([^\|])/g, '| $1');
  normalized = normalized.replace(/([^\|])\|/g, '$1 |');
  
  // 15. Trim trailing whitespace from each line
  normalized = normalized.split('\n').map(line => line.trimEnd()).join('\n');
  
  // 16. Ensure document ends with single newline
  normalized = normalized.trim() + '\n';
  
  return normalized;
}

/**
 * Convert plain text to markdown if no markdown detected
 * @param {string} text - Input text
 * @returns {string} - Markdown formatted text
 */
export function plainTextToMarkdown(text) {
  if (!text) return '';
  
  // Check if text already has markdown
  const hasMarkdown = /^#{1,6}\s|^\s*[-*+]\s|^\s*\d+\.\s|```|\*\*|__|\[.*\]\(.*\)/m.test(text);
  
  if (hasMarkdown) {
    return text; // Already has markdown, don't convert
  }
  
  // Convert plain text to markdown
  let markdown = text;
  
  // Convert CAPS lines to headings (if they're short and standalone)
  markdown = markdown.replace(/^([A-Z\s]{5,50})$/gm, (match) => {
    if (match.trim().length > 5 && match === match.toUpperCase()) {
      return `## ${match.trim()}`;
    }
    return match;
  });
  
  // Convert numbered lines to ordered lists
  markdown = markdown.replace(/^(\d+)\)\s+/gm, '$1. ');
  
  // Add paragraph spacing for better readability
  markdown = markdown.replace(/\n{1}/g, '\n\n');
  markdown = markdown.replace(/\n{3,}/g, '\n\n');
  
  return markdown;
}

/**
 * Sanitize and prepare AI output for rendering
 * @param {string} text - Raw AI output
 * @returns {string} - Sanitized and formatted text
 */
export function prepareAIOutput(text) {
  if (!text) return '';
  
  // Step 1: Basic sanitization
  let prepared = text.trim();
  
  // Step 2: Check if plain text or markdown
  prepared = plainTextToMarkdown(prepared);
  
  // Step 3: Normalize markdown
  prepared = normalizeAIOutput(prepared);
  
  // Step 4: Final cleanup
  prepared = prepared.trim();
  
  return prepared;
}

/**
 * Extract and format statistics from text
 * @param {string} text - Text containing statistics
 * @returns {Object} - Extracted statistics
 */
export function extractStatistics(text) {
  const stats = {};
  
  // Extract magnitude mentions
  const magnitudeMatch = text.match(/M\s*(\d+\.?\d*)/i);
  if (magnitudeMatch) {
    stats.magnitude = parseFloat(magnitudeMatch[1]);
  }
  
  // Extract depth mentions
  const depthMatch = text.match(/(\d+)\s*km\s+depth/i);
  if (depthMatch) {
    stats.depth = parseInt(depthMatch[1]);
  }
  
  return stats;
}
