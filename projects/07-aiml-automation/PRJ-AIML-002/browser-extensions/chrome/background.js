/**
 * Chrome Extension Background Service Worker
 * Handles tab monitoring and communication with native host
 */

const NATIVE_HOST_NAME = 'com.taborganizer.native_host';
const SYNC_INTERVAL = 5000; // 5 seconds

let nativePort = null;
let isConnected = false;

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Tab Organizer extension installed');
  initializeExtension();
});

// Connect to native messaging host
function connectToNativeHost() {
  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME);

    nativePort.onMessage.addListener((message) => {
      handleNativeMessage(message);
    });

    nativePort.onDisconnect.addListener(() => {
      console.error('Disconnected from native host:', chrome.runtime.lastError);
      isConnected = false;
      nativePort = null;

      // Retry connection after 5 seconds
      setTimeout(connectToNativeHost, 5000);
    });

    // Send connection test
    sendToNativeHost({ type: 'connect', timestamp: Date.now() });
    isConnected = true;

    console.log('Connected to native host');
  } catch (error) {
    console.error('Failed to connect to native host:', error);
    isConnected = false;
  }
}

// Initialize extension
function initializeExtension() {
  // Connect to native host
  connectToNativeHost();

  // Set up periodic sync
  setInterval(syncTabs, SYNC_INTERVAL);

  // Initial tab sync
  syncTabs();
}

// Sync all tabs with native host
async function syncTabs() {
  if (!isConnected) return;

  try {
    const tabs = await chrome.tabs.query({});
    const tabData = await Promise.all(tabs.map(extractTabData));

    sendToNativeHost({
      type: 'tabs_update',
      tabs: tabData,
      timestamp: Date.now(),
    });
  } catch (error) {
    console.error('Failed to sync tabs:', error);
  }
}

// Extract relevant data from tab
async function extractTabData(tab) {
  return {
    id: tab.id.toString(),
    url: tab.url || '',
    title: tab.title || 'Untitled',
    favIconUrl: tab.favIconUrl || '',
    windowId: tab.windowId,
    index: tab.index,
    active: tab.active,
    pinned: tab.pinned,
    audible: tab.audible,
    status: tab.status,
  };
}

// Send message to native host
function sendToNativeHost(message) {
  if (!isConnected || !nativePort) {
    console.warn('Not connected to native host');
    return;
  }

  try {
    nativePort.postMessage(message);
  } catch (error) {
    console.error('Failed to send message to native host:', error);
    isConnected = false;
  }
}

// Handle messages from native host
function handleNativeMessage(message) {
  console.log('Received from native host:', message);

  switch (message.type) {
    case 'organize_request':
      organizeTabs(message.groups);
      break;

    case 'close_tab':
      closeTab(message.tabId);
      break;

    case 'focus_tab':
      focusTab(message.tabId);
      break;

    case 'group_tabs':
      groupTabs(message.tabIds, message.groupName);
      break;

    default:
      console.warn('Unknown message type:', message.type);
  }
}

// Organize tabs into groups
async function organizeTabs(groups) {
  console.log('Organizing tabs into groups:', groups);

  for (const group of groups) {
    await groupTabs(group.tabIds, group.name, group.color);
  }
}

// Group tabs together
async function groupTabs(tabIds, groupName, color) {
  try {
    const tabIdsInt = tabIds.map(id => parseInt(id, 10));

    // Create tab group
    const groupId = await chrome.tabs.group({ tabIds: tabIdsInt });

    // Update group properties
    await chrome.tabGroups.update(groupId, {
      title: groupName,
      color: color || 'blue',
    });

    console.log(`Created group "${groupName}" with ${tabIds.length} tabs`);
  } catch (error) {
    console.error('Failed to group tabs:', error);
  }
}

// Close a tab
async function closeTab(tabId) {
  try {
    await chrome.tabs.remove(parseInt(tabId, 10));
    console.log('Closed tab:', tabId);
  } catch (error) {
    console.error('Failed to close tab:', error);
  }
}

// Focus a tab
async function focusTab(tabId) {
  try {
    const tab = await chrome.tabs.get(parseInt(tabId, 10));
    await chrome.tabs.update(tab.id, { active: true });
    await chrome.windows.update(tab.windowId, { focused: true });
    console.log('Focused tab:', tabId);
  } catch (error) {
    console.error('Failed to focus tab:', error);
  }
}

// Listen for tab events
chrome.tabs.onCreated.addListener((tab) => {
  console.log('Tab created:', tab.id);
  syncTabs();
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    console.log('Tab updated:', tabId);
    syncTabs();
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  console.log('Tab removed:', tabId);
  sendToNativeHost({
    type: 'tab_closed',
    tabId: tabId.toString(),
    timestamp: Date.now(),
  });
});

// Listen for commands
chrome.commands.onCommand.addListener((command) => {
  console.log('Command received:', command);

  if (command === 'organize_tabs') {
    sendToNativeHost({
      type: 'organize_request',
      timestamp: Date.now(),
    });
  }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Message from popup:', message);

  if (message.type === 'get_status') {
    sendResponse({ connected: isConnected });
  } else if (message.type === 'organize_now') {
    sendToNativeHost({
      type: 'organize_request',
      timestamp: Date.now(),
    });
    sendResponse({ success: true });
  }

  return true;
});

console.log('Tab Organizer background script loaded');
