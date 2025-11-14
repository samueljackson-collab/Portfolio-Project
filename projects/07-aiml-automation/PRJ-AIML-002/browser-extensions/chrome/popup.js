/**
 * Chrome Extension Popup Script
 */

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const organizeBtn = document.getElementById('organizeBtn');
const settingsBtn = document.getElementById('settingsBtn');
const tabCount = document.getElementById('tabCount');
const groupCount = document.getElementById('groupCount');
const lastOrganized = document.getElementById('lastOrganized');
const openApp = document.getElementById('openApp');

// Initialize popup
async function initialize() {
  updateStatus();
  updateStats();
  setupEventListeners();
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

  settingsBtn.addEventListener('click', () => {
    // Open settings page
    chrome.runtime.openOptionsPage();
  });

  openApp.addEventListener('click', (e) => {
    e.preventDefault();
    // TODO: Implement deep link to desktop app
    alert('Desktop app integration coming soon!');
  });
}

// Initialize when popup opens
initialize();

// Refresh stats periodically
setInterval(updateStats, 5000);
