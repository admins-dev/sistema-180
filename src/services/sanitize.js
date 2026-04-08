// ═══════════════════════════════════════════════════════════
// Sanitize — Anti-XSS utility for Sistema 180
// Prevents injection via innerHTML
// ═══════════════════════════════════════════════════════════

const ESCAPE_MAP = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
  '`': '&#96;',
};

const ESCAPE_REGEX = /[&<>"'/`]/g;

/**
 * Escape HTML entities to prevent XSS when inserting into innerHTML.
 * @param {string} str - Raw string (potentially from API response)
 * @returns {string} Safe HTML-escaped string
 */
export function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(ESCAPE_REGEX, (char) => ESCAPE_MAP[char] || char);
}

/**
 * Sanitize a string for use inside HTML attributes (onclick, etc.)
 * Escapes quotes and backslashes.
 */
export function escapeAttr(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

/**
 * Strip all HTML tags from a string (for textContent-like safety)
 */
export function stripHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/<[^>]*>/g, '');
}
