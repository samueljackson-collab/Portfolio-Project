/**
 * Popup UI script for Tab Organizer
 */

document.addEventListener('DOMContentLoaded', async () => {
  await initializePopup();
});

/**
 * Initialize the popup UI by loading tab data, rendering categories, and attaching UI event handlers.
 *
 * Shows a loading indicator while it loads statistics and categories, sets up event listeners for user controls,
 * and hides the loading indicator when finished. On error, logs the failure and displays an error status to the user.
 */
async function initializePopup() {
  showLoading(true);

  try {
    // Load tab statistics
    await loadStatistics();

    // Load categories
    await loadCategories();

    // Setup event listeners
    setupEventListeners();

    showLoading(false);
  } catch (error) {
    console.error('Error initializing popup:', error);
    showStatus('Error loading data', 'error');
    showLoading(false);
  }
}

/**
 * Fetches all tabs and tab groups and updates the popup UI with total tabs, total groups, and count of ungrouped tabs.
 *
 * Updates elements with IDs "totalTabs", "totalGroups", and "ungroupedTabs" to display the computed counts.
 */
async function loadStatistics() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_ALL_TABS' });
    const tabs = response.tabs || [];

    // Count groups
    const groups = await chrome.tabGroups.query({});

    // Count ungrouped tabs
    const ungroupedTabs = tabs.filter(tab => tab.groupId === -1 || tab.groupId === chrome.tabGroups.TAB_GROUP_ID_NONE).length;

    // Update UI
    document.getElementById('totalTabs').textContent = tabs.length;
    document.getElementById('totalGroups').textContent = groups.length;
    document.getElementById('ungroupedTabs').textContent = ungroupedTabs;
  } catch (error) {
    console.error('Error loading statistics:', error);
  }
}

/**
 * Loads tab data, tallies counts per predefined category, and updates the categories list in the popup UI.
 *
 * Populates counts for Work, Research, Shopping, Social, Entertainment, and News by categorizing each tab URL and replaces the contents of the element with id "categoriesList" with generated category elements.
 */
async function loadCategories() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_ALL_TABS' });
    const tabs = response.tabs || [];

    // Count tabs by category
    const categoryCounts = {};
    const categories = ['Work', 'Research', 'Shopping', 'Social', 'Entertainment', 'News'];

    for (const category of categories) {
      categoryCounts[category] = 0;
    }

    for (const tab of tabs) {
      const category = await getCategoryFromUrl(tab.url);
      if (category && categoryCounts[category] !== undefined) {
        categoryCounts[category]++;
      }
    }

    // Render categories
    const categoriesList = document.getElementById('categoriesList');
    categoriesList.innerHTML = '';

    for (const [category, count] of Object.entries(categoryCounts)) {
      const categoryElement = createCategoryElement(category, count);
      categoriesList.appendChild(categoryElement);
    }
  } catch (error) {
    console.error('Error loading categories:', error);
  }
}

/**
 * Create a DOM element representing a category with its icon and item count.
 * @param {string} category - Category label displayed and used to select an icon.
 * @param {number} count - Number of items for the category.
 * @returns {HTMLDivElement} A `div` element with class `"category"` containing the category name/icon and a count element.
 */
function createCategoryElement(category, count) {
  const div = document.createElement('div');
  div.className = 'category';

  const nameDiv = document.createElement('div');
  nameDiv.className = 'category-name';
  nameDiv.innerHTML = `
    <span class="category-icon">${getCategoryIcon(category)}</span>
    <span>${category}</span>
  `;

  const countSpan = document.createElement('span');
  countSpan.className = 'category-count';
  countSpan.textContent = count;

  div.appendChild(nameDiv);
  div.appendChild(countSpan);

  return div;
}

/**
 * Get an emoji icon for a given category.
 * @param {string} category - Category name to map to an icon.
 * @returns {string} The emoji representing the category, or a default folder icon (`📁`) if the category is unrecognized.
 */
function getCategoryIcon(category) {
  const icons = {
    'Work': '💼',
    'Research': '📚',
    'Shopping': '🛒',
    'Social': '👥',
    'Entertainment': '🎬',
    'News': '📰'
  };

  return icons[category] || '📁';
}

/**
 * Determine the category label for a given URL based on predefined domain patterns.
 * @param {string} url - The full URL or hostname to classify.
 * @returns {string|null} The matching category name ('Work', 'Research', 'Shopping', 'Social', 'Entertainment', 'News') if a domain pattern matches, `null` otherwise.
 */
async function getCategoryFromUrl(url) {
  const patterns = {
    'Work': [
      'github.com', 'gitlab.com', 'stackoverflow.com',
      'docs.google.com', 'notion.so', 'slack.com',
      'teams.microsoft.com', 'zoom.us'
    ],
    'Research': [
      'wikipedia.org', 'scholar.google.com', 'arxiv.org',
      'medium.com', 'dev.to'
    ],
    'Shopping': [
      'amazon.com', 'ebay.com', 'etsy.com',
      'shopify.com', 'walmart.com'
    ],
    'Social': [
      'facebook.com', 'twitter.com', 'instagram.com',
      'linkedin.com', 'reddit.com'
    ],
    'Entertainment': [
      'youtube.com', 'netflix.com', 'spotify.com',
      'twitch.tv', 'hulu.com'
    ],
    'News': [
      'news.google.com', 'bbc.com', 'cnn.com',
      'reuters.com', 'nytimes.com'
    ]
  };

  for (const [category, domains] of Object.entries(patterns)) {
    if (domains.some(domain => url.includes(domain))) {
      return category;
    }
  }

  return null;
}

/**
 * Attach click handlers to popup buttons to trigger auto-grouping, syncing, and opening the desktop app.
 *
 * The auto-group handler displays a syncing status, initiates grouping of tabs, refreshes statistics and categories, and shows a success or error status. The sync handler requests a background sync and shows a success or error status. The open-app handler requests the background to open the desktop application and shows a brief status message.
 */
function setupEventListeners() {
  // Auto-group button
  document.getElementById('autoGroupBtn').addEventListener('click', async () => {
    showStatus('Auto-grouping tabs...', 'syncing');
    try {
      await autoGroupAllTabs();
      await loadStatistics();
      await loadCategories();
      showStatus('Tabs grouped successfully!', 'success');
      setTimeout(() => showStatus(''), 3000);
    } catch (error) {
      console.error('Error auto-grouping:', error);
      showStatus('Error grouping tabs', 'error');
    }
  });

  // Sync button
  document.getElementById('syncBtn').addEventListener('click', async () => {
    showStatus('Syncing...', 'syncing');
    try {
      // Send sync request to background
      await chrome.runtime.sendMessage({ type: 'SYNC_TABS' });
      showStatus('Synced successfully!', 'success');
      setTimeout(() => showStatus(''), 3000);
    } catch (error) {
      console.error('Error syncing:', error);
      showStatus('Error syncing', 'error');
    }
  });

  // Open app button
  document.getElementById('openAppBtn').addEventListener('click', () => {
    showStatus('Opening desktop app...');
    // This would open the desktop app via native messaging
    chrome.runtime.sendMessage({ type: 'OPEN_DESKTOP_APP' });
  });
}

/**
 * Group open tabs by detected category and request creation of corresponding tab groups.
 *
 * Fetches all tabs, determines a category for each tab URL, aggregates tab IDs by category,
 * and sends a background message to create a group for each category containing one or more tabs.
 * Uncategorized tabs are ignored.
 */
async function autoGroupAllTabs() {
  const response = await chrome.runtime.sendMessage({ type: 'GET_ALL_TABS' });
  const tabs = response.tabs || [];

  // Group by category
  const tabsByCategory = {};

  for (const tab of tabs) {
    const category = await getCategoryFromUrl(tab.url);
    if (category) {
      if (!tabsByCategory[category]) {
        tabsByCategory[category] = [];
      }
      tabsByCategory[category].push(tab.id);
    }
  }

  // Create groups
  for (const [category, tabIds] of Object.entries(tabsByCategory)) {
    if (tabIds.length > 0) {
      await chrome.runtime.sendMessage({
        type: 'CREATE_GROUP',
        name: category,
        tabIds: tabIds,
        color: getCategoryColor(category)
      });
    }
  }
}

/**
 * Map a category name to its display color.
 *
 * @param {string} category - The category name (e.g., "Work", "Research").
 * @returns {string} The color associated with the category, or 'grey' if unknown.
 */
function getCategoryColor(category) {
  const colors = {
    'Work': 'blue',
    'Research': 'purple',
    'Shopping': 'pink',
    'Social': 'green',
    'Entertainment': 'orange',
    'News': 'red'
  };

  return colors[category] || 'grey';
}

/**
 * Toggle visibility between the loading indicator and the main content.
 * @param {boolean} show - `true` to display the loading indicator and hide the content, `false` to hide the loading indicator and show the content.
 */
function showLoading(show) {
  document.getElementById('loading').style.display = show ? 'block' : 'none';
  document.getElementById('content').style.display = show ? 'none' : 'block';
}

/**
 * Display a status message in the popup and apply an optional status style.
 * @param {string} message - Text to show in the status element.
 * @param {string} [type] - Optional CSS modifier applied to the status element (e.g., "syncing", "success", "error").
 */
function showStatus(message, type = '') {
  const statusElement = document.getElementById('status');
  statusElement.textContent = message;
  statusElement.className = `status ${type}`;
}