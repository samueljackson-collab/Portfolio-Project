/**
 * Background service worker for Tab Organizer Chrome Extension
 *
 * IMPORTANT: For Manifest V3, all event listeners must be registered at the
 * top level (synchronously) so Chrome can wake the service worker when events occur.
 */

const NATIVE_HOST_NAME = 'com.taborganizer.native';

// Register all event listeners at top level (required for Manifest V3)
// These listeners persist across service worker restarts

// Tab created
chrome.tabs.onCreated.addListener(handleTabCreated);

// Tab updated
chrome.tabs.onUpdated.addListener(handleTabUpdated);

// Tab removed
chrome.tabs.onRemoved.addListener(handleTabRemoved);

// Tab activated
chrome.tabs.onActivated.addListener(handleTabActivated);

// Window focus changed
chrome.windows.onFocusChanged.addListener(handleWindowFocusChanged);

// Handle alarms
chrome.alarms.onAlarm.addListener(handleAlarm);

// Handle messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender).then(sendResponse);
  return true; // Keep channel open for async response
});

// Initialize extension on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('Tab Organizer installed');
  initializeExtension();
});

// Initialize extension state
async function initializeExtension() {
  // Set default settings
  const settings = await chrome.storage.sync.get('settings');
  if (!settings.settings) {
    await chrome.storage.sync.set({
      settings: {
        autoGroup: true,
        syncEnabled: true,
        notificationsEnabled: true,
        minConfidenceScore: 0.6
      }
    });
  }

  // Start periodic sync
  chrome.alarms.create('syncTabs', { periodInMinutes: 5 });
}

// Handle tab created
async function handleTabCreated(tab) {
  console.log('Tab created:', tab.id, tab.url);

  // Send to native app
  await sendToNativeApp({
    type: 'TAB_CREATED',
    tab: serializeTab(tab),
    timestamp: new Date().toISOString()
  });

  // Check for auto-grouping
  const settings = await getSettings();
  if (settings.autoGroup) {
    await autoGroupTab(tab);
  }
}

// Handle tab updated
async function handleTabUpdated(tabId, changeInfo, tab) {
  // Only process when loading is complete
  if (changeInfo.status === 'complete') {
    console.log('Tab updated:', tabId, tab.url);

    await sendToNativeApp({
      type: 'TAB_UPDATED',
      tab: serializeTab(tab),
      changeInfo: changeInfo,
      timestamp: new Date().toISOString()
    });
  }
}

// Handle tab removed
async function handleTabRemoved(tabId, removeInfo) {
  console.log('Tab removed:', tabId);

  await sendToNativeApp({
    type: 'TAB_REMOVED',
    tabId: tabId,
    removeInfo: removeInfo,
    timestamp: new Date().toISOString()
  });
}

// Handle tab activated
async function handleTabActivated(activeInfo) {
  const tab = await chrome.tabs.get(activeInfo.tabId);

  await sendToNativeApp({
    type: 'TAB_ACTIVATED',
    tab: serializeTab(tab),
    timestamp: new Date().toISOString()
  });
}

// Handle window focus changed
async function handleWindowFocusChanged(windowId) {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    return;
  }

  const tabs = await chrome.tabs.query({ windowId: windowId, active: true });
  if (tabs.length > 0) {
    await sendToNativeApp({
      type: 'WINDOW_FOCUS_CHANGED',
      tab: serializeTab(tabs[0]),
      windowId: windowId,
      timestamp: new Date().toISOString()
    });
  }
}

// Get all tabs
async function getAllTabs() {
  const tabs = await chrome.tabs.query({});
  return tabs.map(serializeTab);
}

// Serialize tab for transmission
function serializeTab(tab) {
  return {
    id: tab.id,
    title: tab.title,
    url: tab.url,
    favIconUrl: tab.favIconUrl,
    active: tab.active,
    pinned: tab.pinned,
    index: tab.index,
    windowId: tab.windowId,
    groupId: tab.groupId,
    status: tab.status
  };
}

// Auto-group tab based on category
async function autoGroupTab(tab) {
  try {
    // Get or create category from URL
    const category = await getCategoryFromUrl(tab.url);
    if (!category) return;

    // Find or create tab group for this category
    const groups = await chrome.tabGroups.query({ title: category });

    let groupId;
    if (groups.length > 0) {
      groupId = groups[0].id;
    } else {
      // Create new group
      groupId = await chrome.tabs.group({ tabIds: [tab.id] });
      await chrome.tabGroups.update(groupId, {
        title: category,
        color: getCategoryColor(category)
      });
      return;
    }

    // Add tab to existing group
    await chrome.tabs.group({ tabIds: [tab.id], groupId: groupId });
  } catch (error) {
    console.error('Error auto-grouping tab:', error);
  }
}

// Get category from URL using pattern matching
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

// Send message to native app
async function sendToNativeApp(message) {
  try {
    const response = await chrome.runtime.sendNativeMessage(
      NATIVE_HOST_NAME,
      message
    );
    console.log('Native app response:', response);
    return response;
  } catch (error) {
    console.error('Error sending to native app:', error);
    return null;
  }
}

// Handle messages (implementation for listener registered at top)
async function handleMessage(request, sender) {
  console.log('Received message:', request.type);

  switch (request.type) {
    case 'GET_ALL_TABS':
      return { tabs: await getAllTabs() };

    case 'GET_ACTIVE_TAB':
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      return { tab: serializeTab(activeTab) };

    case 'CREATE_GROUP':
      const groupId = await chrome.tabs.group({ tabIds: request.tabIds });
      await chrome.tabGroups.update(groupId, {
        title: request.name,
        color: request.color || 'grey'
      });
      return { groupId };

    case 'CLOSE_TAB':
      await chrome.tabs.remove(request.tabId);
      return { success: true };

    case 'FOCUS_TAB':
      await chrome.tabs.update(request.tabId, { active: true });
      return { success: true };

    case 'UPDATE_TAB':
      await chrome.tabs.update(request.tabId, {
        url: request.url,
        pinned: request.pinned
      });
      return { success: true };

    case 'PING':
      return { pong: true };

    default:
      return { error: 'Unknown message type' };
  }
}

// Handle alarms (implementation for listener registered at top)
async function handleAlarm(alarm) {
  if (alarm.name === 'syncTabs') {
    console.log('Syncing tabs...');
    const tabs = await getAllTabs();
    await sendToNativeApp({
      type: 'SYNC_TABS',
      tabs: tabs,
      timestamp: new Date().toISOString()
    });
  }
}

// Get settings
async function getSettings() {
  const result = await chrome.storage.sync.get('settings');
  return result.settings || {};
}

// Update settings
async function updateSettings(newSettings) {
  const currentSettings = await getSettings();
  const updatedSettings = { ...currentSettings, ...newSettings };
  await chrome.storage.sync.set({ settings: updatedSettings });
  return updatedSettings;
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    serializeTab,
    getCategoryFromUrl,
    getCategoryColor,
    getSettings,
    updateSettings
  };
}
