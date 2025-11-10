/**
 * Background service worker for Tab Organizer Chrome Extension
 */

const NATIVE_HOST_NAME = 'com.taborganizer.native';

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Tab Organizer installed');
  initializeExtension();
});

/**
 * Initialize extension defaults, start tab/window event listeners, and schedule periodic tab synchronization.
 *
 * Ensures default settings exist in chrome.storage.sync (autoGroup: true, syncEnabled: true, notificationsEnabled: true, minConfidenceScore: 0.6), registers tab and window listeners, and creates a repeating 'syncTabs' alarm that fires every 5 minutes.
 */
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

  // Start listening to tab events
  startTabListeners();

  // Start periodic sync
  chrome.alarms.create('syncTabs', { periodInMinutes: 5 });
}

/**
 * Registers Chrome event listeners for tab lifecycle and window focus events used by the extension.
 *
 * Sets up handlers for tab creation, tab updates, tab removal, tab activation, and window focus changes so the extension can react to tab and window lifecycle events.
 */
function startTabListeners() {
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
}

/**
 * Handle a newly created tab by notifying the native app and performing auto-grouping if enabled.
 *
 * Sends a `TAB_CREATED` message containing the serialized tab and a timestamp to the native host,
 * then loads settings and, if `autoGroup` is enabled, attempts to categorize and group the tab.
 *
 * @param {chrome.tabs.Tab} tab - The created tab object.
 */
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

/**
 * Send a `TAB_UPDATED` event to the native app when a tab finishes loading.
 *
 * Processes the update only if `changeInfo.status` is `"complete"`, then serializes
 * the tab and forwards the update with a timestamp.
 *
 * @param {number} tabId - The ID of the updated tab.
 * @param {Object} changeInfo - The change information for the tab; checked for `status`.
 * @param {chrome.tabs.Tab} tab - The full tab object to serialize and send.
 */
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

/**
 * Notify the native host that a tab was removed.
 * @param {number} tabId - ID of the removed tab.
 * @param {Object} removeInfo - Details about the removal (e.g., windowId, isWindowClosing).
 */
async function handleTabRemoved(tabId, removeInfo) {
  console.log('Tab removed:', tabId);

  await sendToNativeApp({
    type: 'TAB_REMOVED',
    tabId: tabId,
    removeInfo: removeInfo,
    timestamp: new Date().toISOString()
  });
}

/**
 * Notify the native host that a tab was activated.
 * @param {{tabId: number, windowId?: number}} activeInfo - Activation details containing the activated tab's `tabId` and optional `windowId`.
 */
async function handleTabActivated(activeInfo) {
  const tab = await chrome.tabs.get(activeInfo.tabId);

  await sendToNativeApp({
    type: 'TAB_ACTIVATED',
    tab: serializeTab(tab),
    timestamp: new Date().toISOString()
  });
}

/**
 * Sends the newly focused window's active tab to the native app when window focus changes.
 *
 * If `windowId` equals `chrome.windows.WINDOW_ID_NONE` no action is taken. Otherwise the active
 * tab for the given window is retrieved and its serialized representation is sent to the native host
 * with a `WINDOW_FOCUS_CHANGED` message and timestamp.
 * @param {number} windowId - The Chrome window ID reported by the focus change event.
 */
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

/**
 * Retrieve all open tabs in the browser as serialized objects.
 * @returns {Array<Object>} An array of serialized tab objects containing `id`, `title`, `url`, `favIconUrl`, `active`, `pinned`, `index`, `windowId`, `groupId`, and `status`.
 */
async function getAllTabs() {
  const tabs = await chrome.tabs.query({});
  return tabs.map(serializeTab);
}

/**
 * Convert a Chrome Tab object into a plain serializable object with commonly used tab properties.
 * @param {chrome.tabs.Tab} tab - The tab to serialize.
 * @returns {{id:number, title:string, url:string, favIconUrl?:string, active:boolean, pinned:boolean, index:number, windowId:number, groupId:number, status?:string}} An object containing the tab's id, title, url, favIconUrl, active, pinned, index, windowId, groupId, and status.
 */
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

/**
 * Places a tab into a tab group determined from its URL, creating and naming the group (with a category color) if none exists.
 *
 * @param {chrome.tabs.Tab} tab - The tab to categorize and add to a group; must include `id` and `url`.
 */
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

/**
 * Determine the category name for a URL based on domain pattern matching.
 *
 * @param {string} url - The URL or hostname to classify.
 * @returns {string|null} The matched category name (e.g., "Work", "Social") if a domain pattern matches, `null` if no category matches.
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
 * Map a tab category name to its display color.
 * @param {string} category - Category name (e.g., "Work", "Research", "Shopping", "Social", "Entertainment", "News").
 * @returns {string} The color name associated with the category, or `'grey'` if the category is unrecognized.
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
 * Sends a message to the configured native host and returns its response.
 * @param {any} message - The payload to deliver to the native application.
 * @returns {any|null} The native app's response object, or `null` if sending failed.
 */
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

// Handle messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender).then(sendResponse);
  return true; // Keep channel open for async response
});

/**
 * Handle runtime messages and perform tab and group operations based on the request type.
 *
 * @param {Object} request - Incoming message. Expected shapes vary by `request.type`:
 *   - { type: 'GET_ALL_TABS' }
 *   - { type: 'GET_ACTIVE_TAB' }
 *   - { type: 'CREATE_GROUP', tabIds: number[]|number, name?: string, color?: string }
 *   - { type: 'CLOSE_TAB', tabId: number }
 *   - { type: 'FOCUS_TAB', tabId: number }
 *   - { type: 'UPDATE_TAB', tabId: number, url?: string, pinned?: boolean }
 *   - { type: 'PING' }
 * @returns {Object} One of:
 *   - { tabs: Array<Object> } for `GET_ALL_TABS`
 *   - { tab: Object } for `GET_ACTIVE_TAB`
 *   - { groupId: number|string } for `CREATE_GROUP`
 *   - { success: true } for `CLOSE_TAB`, `FOCUS_TAB`, `UPDATE_TAB`
 *   - { pong: true } for `PING`
 *   - { error: string } for unknown or unsupported message types
 */
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

// Handle alarms
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'syncTabs') {
    console.log('Syncing tabs...');
    const tabs = await getAllTabs();
    await sendToNativeApp({
      type: 'SYNC_TABS',
      tabs: tabs,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Retrieve the extension's stored settings from chrome.storage.sync.
 * @returns {Object} An object containing saved settings (for example: `autoGroup`, `syncEnabled`, `notificationsEnabled`, `minConfidenceScore`). Returns an empty object if no settings are stored.
 */
async function getSettings() {
  const result = await chrome.storage.sync.get('settings');
  return result.settings || {};
}

/**
 * Merge provided settings into the stored settings and persist the result.
 *
 * @param {Object} newSettings - Partial settings to merge into the existing settings; properties in this object overwrite existing values.
 * @returns {Object} The resulting settings object after merging and saving.
 */
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