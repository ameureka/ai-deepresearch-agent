/**
 * Research utility functions for detecting and extracting research-related content
 *
 * These functions are used to identify when AI suggests research and extract
 * the research query from AI messages.
 */

/**
 * Research keywords to detect in AI messages
 * Both English and Chinese keywords are supported
 */
const RESEARCH_KEYWORDS = [
  // English keywords
  'research',
  'investigate',
  'study',
  'analyze',
  'explore',
  'examine',
  'look into',
  'find out',
  'gather information',

  // Chinese keywords
  '研究',
  '调查',
  '探索',
  '分析',
  '查找',
  '了解',
  '深入研究',
] as const;

/**
 * Detects if a message contains research-related keywords
 *
 * @param message - The message content to check (typically from AI)
 * @returns true if research keywords are detected
 *
 * @example
 * ```typescript
 * const aiMessage = "I can research quantum computing for you.";
 * const hasResearch = detectResearchKeywords(aiMessage); // true
 * ```
 */
export function detectResearchKeywords(message: string): boolean {
  if (!message || typeof message !== 'string') {
    return false;
  }

  const lowerMessage = message.toLowerCase();

  return RESEARCH_KEYWORDS.some(keyword =>
    lowerMessage.includes(keyword.toLowerCase())
  );
}

/**
 * Extracts a research query from an AI message
 *
 * This function attempts to extract the main topic or question that should
 * be researched from an AI message containing research suggestions.
 *
 * @param message - The AI message content
 * @returns The extracted research query or the full message if extraction fails
 *
 * @example
 * ```typescript
 * const aiMessage = "I can research quantum computing for you. Would you like me to start?";
 * const query = extractResearchQuery(aiMessage); // "quantum computing"
 * ```
 */
export function extractResearchQuery(message: string): string {
  if (!message || typeof message !== 'string') {
    return '';
  }

  // Common patterns to extract research topics
  const patterns = [
    // "research [topic]"
    /research\s+(?:about\s+)?(?:on\s+)?(.+?)(?:\s+for\s+you|\?|\.|\n|$)/i,
    // "investigate [topic]"
    /investigate\s+(.+?)(?:\s+for\s+you|\?|\.|\n|$)/i,
    // "study [topic]"
    /study\s+(.+?)(?:\s+for\s+you|\?|\.|\n|$)/i,
    // "analyze [topic]"
    /analyze\s+(.+?)(?:\s+for\s+you|\?|\.|\n|$)/i,
    // "研究 [topic]"
    /研究\s*(.+?)(?:吗|\?|。|\n|$)/,
    // "调查 [topic]"
    /调查\s*(.+?)(?:吗|\?|。|\n|$)/,
  ];

  // Try each pattern
  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      const query = match[1].trim();
      // Clean up common suffixes
      return query
        .replace(/\s+(for you|please|now)$/i, '')
        .replace(/[。？！，、]$/, '')
        .trim();
    }
  }

  // Fallback: return first sentence or first 100 characters
  const firstSentence = message.split(/[.!?。！？]/)[0];
  if (firstSentence && firstSentence.length < 100) {
    return firstSentence.trim();
  }

  return message.slice(0, 100).trim() + (message.length > 100 ? '...' : '');
}

/**
 * Validates if a research query is suitable for processing
 *
 * @param query - The research query to validate
 * @returns true if the query is valid and suitable for research
 *
 * @example
 * ```typescript
 * validateResearchQuery("quantum computing"); // true
 * validateResearchQuery("hi"); // false (too short)
 * validateResearchQuery(""); // false (empty)
 * ```
 */
export function validateResearchQuery(query: string): boolean {
  if (!query || typeof query !== 'string') {
    return false;
  }

  const trimmed = query.trim();

  // Must be at least 3 characters
  if (trimmed.length < 3) {
    return false;
  }

  // Must not be too long (reasonable limit)
  if (trimmed.length > 500) {
    return false;
  }

  // Must contain at least one letter (not just numbers/symbols)
  if (!/[a-zA-Z\u4e00-\u9fa5]/.test(trimmed)) {
    return false;
  }

  return true;
}
