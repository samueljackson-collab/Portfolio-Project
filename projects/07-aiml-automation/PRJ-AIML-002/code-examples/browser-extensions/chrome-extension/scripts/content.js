/**
 * Content script for Tab Organizer
 * Injected into web pages to analyze content
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleContentMessage(request).then(sendResponse);
  return true; // Keep channel open for async response
});

/**
 * Route and handle content-script requests from the background script.
 * @param {Object} request - Message object received from the background script.
 * @param {string} request.type - The request type: 'ANALYZE_PAGE', 'GET_PAGE_CONTENT', or 'GET_PAGE_KEYWORDS'.
 * @returns {Object} The response for the given request type: for 'ANALYZE_PAGE' the page analysis object; for 'GET_PAGE_CONTENT' an object with `content` (string); for 'GET_PAGE_KEYWORDS' an object with `keywords` (string[]); otherwise an object with `error` (string).
 */
async function handleContentMessage(request) {
  switch (request.type) {
    case 'ANALYZE_PAGE':
      return await analyzePage();

    case 'GET_PAGE_CONTENT':
      return { content: getPageContent() };

    case 'GET_PAGE_KEYWORDS':
      return { keywords: extractKeywords() };

    default:
      return { error: 'Unknown message type' };
  }
}

/**
 * Build a summary analysis of the current page.
 *
 * @returns {{content: string, keywords: string[], metadata: Object, url: string, title: string}} An object containing the page analysis:
 *   - content: cleaned textual content extracted from the page (truncated when necessary).
 *   - keywords: ordered list of extracted keywords.
 *   - metadata: collected meta tags and parsed schema data.
 *   - url: the current page URL.
 *   - title: the document title.
 */
async function analyzePage() {
  const content = getPageContent();
  const keywords = extractKeywords();
  const metadata = getPageMetadata();

  return {
    content: content,
    keywords: keywords,
    metadata: metadata,
    url: window.location.href,
    title: document.title
  };
}

/**
 * Extracts the main textual content of the page body, excluding common non-content elements.
 * @returns {string} The cleaned page text with collapsed whitespace, truncated to 5000 characters; empty string if the document body is absent.
 */
function getPageContent() {
  // Get main content, excluding scripts and styles
  const body = document.body;
  if (!body) return '';

  const clone = body.cloneNode(true);

  // Remove scripts, styles, and other non-content elements
  const unwantedElements = clone.querySelectorAll('script, style, noscript, iframe, nav, footer, aside');
  unwantedElements.forEach(el => el.remove());

  // Get text content
  const text = clone.textContent || '';

  // Clean up whitespace
  return text.replace(/\s+/g, ' ').trim().slice(0, 5000); // Limit to 5000 chars
}

/**
 * Produce a list of the page's most frequent keywords.
 *
 * Keywords are derived from the page's main text: text is lowercased, common stop words are removed,
 * words of length 3 or less are ignored, and the remaining words are ranked by frequency.
 * The function returns up to the top 20 keywords ordered from highest to lowest frequency.
 * @returns {string[]} Top keywords found on the page ordered by descending frequency (up to 20).
 */
function extractKeywords() {
  const text = getPageContent().toLowerCase();

  // Remove common stop words
  const stopWords = new Set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
    'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
    'do', 'at', 'this', 'but', 'his', 'by', 'from', 'is', 'was',
    'are', 'been', 'has', 'had', 'were', 'said', 'can', 'will'
  ]);

  // Extract words
  const words = text.match(/\b\w+\b/g) || [];

  // Count word frequency
  const wordFreq = {};
  for (const word of words) {
    if (word.length > 3 && !stopWords.has(word)) {
      wordFreq[word] = (wordFreq[word] || 0) + 1;
    }
  }

  // Sort by frequency and return top keywords
  const sortedWords = Object.entries(wordFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20)
    .map(([word]) => word);

  return sortedWords;
}

/**
 * Collects page metadata from meta tags, Open Graph tags, and JSON-LD schema blocks.
 *
 * Searches the document for meta[name] or meta[property] tags and adds their content to a metadata map keyed by the tag's name or property. Also collects meta[property^="og:"] entries and parses any script[type="application/ld+json"] blocks into an array attached as `metadata.schema` when present (JSON parse errors are ignored).
 *
 * @returns {Object} An object mapping meta tag names/properties to their content. If JSON-LD schema blocks were found and successfully parsed, includes a `schema` array of parsed objects.
 */
function getPageMetadata() {
  const metadata = {};

  // Meta tags
  const metaTags = document.querySelectorAll('meta');
  metaTags.forEach(tag => {
    const name = tag.getAttribute('name') || tag.getAttribute('property');
    const content = tag.getAttribute('content');
    if (name && content) {
      metadata[name] = content;
    }
  });

  // Open Graph tags
  const ogTags = document.querySelectorAll('meta[property^="og:"]');
  ogTags.forEach(tag => {
    const property = tag.getAttribute('property');
    const content = tag.getAttribute('content');
    if (property && content) {
      metadata[property] = content;
    }
  });

  // Schema.org structured data
  const schemaScripts = document.querySelectorAll('script[type="application/ld+json"]');
  const schemaData = [];
  schemaScripts.forEach(script => {
    try {
      schemaData.push(JSON.parse(script.textContent));
    } catch (e) {
      // Ignore parse errors
    }
  });

  if (schemaData.length > 0) {
    metadata.schema = schemaData;
  }

  return metadata;
}

/**
 * Determine the page's category by matching weighted keyword occurrences in the URL, title, and main content.
 *
 * Matches predefined category keyword sets and scores each category with weights for URL (highest), title, and content (lowest); returns the category with the highest positive score or `'other'` if none match.
 *
 * @returns {string} The detected category: one of `'work'`, `'research'`, `'shopping'`, `'social'`, `'entertainment'`, `'news'`, or `'other'`.
 */
function detectCategory() {
  const url = window.location.href.toLowerCase();
  const title = document.title.toLowerCase();
  const content = getPageContent().toLowerCase();

  // Category indicators
  const categories = {
    work: ['github', 'code', 'api', 'documentation', 'developer', 'programming'],
    research: ['wikipedia', 'research', 'study', 'paper', 'journal', 'academic'],
    shopping: ['cart', 'buy', 'price', 'product', 'shop', 'order'],
    social: ['social', 'friend', 'post', 'share', 'like', 'comment'],
    entertainment: ['video', 'watch', 'movie', 'music', 'play', 'stream'],
    news: ['news', 'article', 'breaking', 'latest', 'report']
  };

  const scores = {};

  // Score each category
  for (const [category, keywords] of Object.entries(categories)) {
    let score = 0;

    for (const keyword of keywords) {
      if (url.includes(keyword)) score += 3;
      if (title.includes(keyword)) score += 2;
      if (content.includes(keyword)) score += 1;
    }

    scores[category] = score;
  }

  // Return category with highest score
  const maxScore = Math.max(...Object.values(scores));
  if (maxScore > 0) {
    return Object.keys(scores).find(cat => scores[cat] === maxScore);
  }

  return 'other';
}

// Send page analysis to background on load
if (document.readyState === 'complete') {
  sendAnalysisToBackground();
} else {
  window.addEventListener('load', sendAnalysisToBackground);
}

/**
 * Sends a page analysis to the extension background script.
 *
 * Runs the page analysis and dispatches a `PAGE_ANALYZED` message containing the analysis.
 * Any errors encountered during analysis or messaging are caught and logged to the console.
 */
async function sendAnalysisToBackground() {
  try {
    const analysis = await analyzePage();
    chrome.runtime.sendMessage({
      type: 'PAGE_ANALYZED',
      analysis: analysis
    });
  } catch (error) {
    console.error('Error analyzing page:', error);
  }
}

// Log content script loaded
console.log('Tab Organizer content script loaded');