/**
 * Chrome Extension Popup Script
 */

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const organizeBtn = document.getElementById('organizeBtn');
const syncBtn = document.getElementById('syncBtn');
const settingsBtn = document.getElementById('settingsBtn');
const tabCount = document.getElementById('tabCount');
const groupCount = document.getElementById('groupCount');
const lastOrganized = document.getElementById('lastOrganized');
const openApp = document.getElementById('openApp');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

// Initialize popup
async function initialize() {
  updateStatus();
  updateStats();
  setupEventListeners();
  renderSearchResults('');
}

// Update connection status
async function updateStatus() {
  const response = await chrome.runtime.sendMessage({ type: 'get_status' });

  if (response.connected) {
    statusIndicator.classList.add('connected');
    statusText.textContent = 'Connected';
  } else {
    statusIndicator.classList.remove('connected');
    statusText.textContent = 'Disconnected';
  }
}

// Update statistics
async function updateStats() {
  try {
    // Get tab count
    const tabs = await chrome.tabs.query({});
    tabCount.textContent = tabs.length;

    // Get group count
    const groups = await chrome.tabGroups.query({});
    groupCount.textContent = groups.length;

    // Get last organized time from storage
    const result = await chrome.storage.local.get(['lastOrganized']);
    if (result.lastOrganized) {
      const date = new Date(result.lastOrganized);
      lastOrganized.textContent = formatRelativeTime(date);
    }
  } catch (error) {
    console.error('Failed to update stats:', error);
  }
}

// Format relative time
function formatRelativeTime(date) {
  const now = new Date();
  const diff = now - date;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return 'Just now';
  } else if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else {
    return `${days}d ago`;
  }
}

// Setup event listeners
function setupEventListeners() {
  organizeBtn.addEventListener('click', async () => {
    organizeBtn.disabled = true;
    organizeBtn.textContent = 'Organizing...';

    try {
      await chrome.runtime.sendMessage({ type: 'organize_now' });
      await chrome.storage.local.set({ lastOrganized: Date.now() });

      organizeBtn.textContent = 'Done!';
      setTimeout(() => {
        organizeBtn.textContent = 'Organize Tabs Now';
        organizeBtn.disabled = false;
        updateStats();
      }, 2000);
    } catch (error) {
      console.error('Failed to organize tabs:', error);
      organizeBtn.textContent = 'Error';
      setTimeout(() => {
        organizeBtn.textContent = 'Organize Tabs Now';
        organizeBtn.disabled = false;
      }, 2000);
    }
  });

  syncBtn.addEventListener('click', async () => {
    syncBtn.disabled = true;
    syncBtn.textContent = 'Syncing...';

    try {
      await chrome.runtime.sendMessage({ type: 'sync_now' });
      syncBtn.textContent = 'Synced!';
      setTimeout(() => {
        syncBtn.textContent = 'Sync Now';
        syncBtn.disabled = false;
      }, 1500);
    } catch (error) {
      console.error('Failed to sync:', error);
      syncBtn.textContent = 'Sync failed';
      setTimeout(() => {
        syncBtn.textContent = 'Sync Now';
        syncBtn.disabled = false;
      }, 2000);
    }
  });

  settingsBtn.addEventListener('click', () => {
    // Open settings page
    chrome.runtime.openOptionsPage();
  });

  openApp.addEventListener('click', (e) => {
    e.preventDefault();
    openApp.textContent = 'Opening...';
    chrome.runtime.sendMessage({ type: 'open_desktop_app' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Failed to open app:', chrome.runtime.lastError);
        alert('Unable to reach the desktop app.');
      } else if (!response?.success) {
        alert('Desktop app not available.');
      }
      openApp.textContent = 'Open Desktop App';
    });
  });

  searchInput.addEventListener('input', async (event) => {
    const query = event.target.value.trim();
    await renderSearchResults(query);
  });
}

async function renderSearchResults(query) {
  searchResults.innerHTML = '';

  if (!query) {
    const empty = document.createElement('div');
    empty.className = 'search-item';
    empty.textContent = 'Type to search tabs...';
    searchResults.appendChild(empty);
    return;
  }

  try {
    const tabs = await chrome.tabs.query({});
    const filtered = tabs.filter((tab) => {
      const text = `${tab.title || ''} ${tab.url || ''}`.toLowerCase();
      return text.includes(query.toLowerCase());
    });

    const limited = filtered.slice(0, 6);
    if (limited.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'search-item';
      empty.textContent = 'No matching tabs.';
      searchResults.appendChild(empty);
      return;
    }

    limited.forEach((tab) => {
      const item = document.createElement('div');
      item.className = 'search-item';
      item.addEventListener('click', () => {
        chrome.tabs.update(tab.id, { active: true });
        chrome.windows.update(tab.windowId, { focused: true });
      });

      const title = document.createElement('div');
      title.className = 'search-item-title';
      title.textContent = tab.title || 'Untitled Tab';

      const subtitle = document.createElement('div');
      subtitle.className = 'search-item-subtitle';
      subtitle.textContent = tab.url || '';

      item.appendChild(title);
      item.appendChild(subtitle);
      searchResults.appendChild(item);
    });
  } catch (error) {
    console.error('Failed to search tabs:', error);
  }
}

// Initialize when popup opens
initialize();

// Refresh stats periodically
setInterval(updateStats, 5000);
