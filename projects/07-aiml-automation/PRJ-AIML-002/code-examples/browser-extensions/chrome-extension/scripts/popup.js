/**
 * Popup UI script for Tab Organizer
 */

document.addEventListener('DOMContentLoaded', async () => {
  await initializePopup();
});

// Initialize popup
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

// Load statistics
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

// Load categories
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

// Create category element
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

// Get category icon
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

// Get category from URL
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

// Setup event listeners
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

// Auto-group all tabs
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

// Get category color
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

// Show/hide loading
function showLoading(show) {
  document.getElementById('loading').style.display = show ? 'block' : 'none';
  document.getElementById('content').style.display = show ? 'none' : 'block';
}

// Show status message
function showStatus(message, type = '') {
  const statusElement = document.getElementById('status');
  statusElement.textContent = message;
  statusElement.className = `status ${type}`;
}
