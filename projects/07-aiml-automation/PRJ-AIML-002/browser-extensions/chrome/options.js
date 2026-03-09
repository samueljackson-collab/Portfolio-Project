const SETTINGS_KEY = 'syncSettings';
const DEFAULT_SETTINGS = {
  syncEnabled: true,
  syncIntervalSeconds: 5,
};

const syncEnabledInput = document.getElementById('syncEnabled');
const syncIntervalInput = document.getElementById('syncInterval');
const saveBtn = document.getElementById('saveBtn');
const status = document.getElementById('status');
const openDesktop = document.getElementById('openDesktop');

async function loadSettings() {
  const stored = await chrome.storage.sync.get({
    [SETTINGS_KEY]: DEFAULT_SETTINGS,
  });

  const settings = {
    ...DEFAULT_SETTINGS,
    ...(stored[SETTINGS_KEY] || {}),
  };

  syncEnabledInput.checked = settings.syncEnabled;
  syncIntervalInput.value = settings.syncIntervalSeconds;
}

async function saveSettings() {
  const settings = {
    syncEnabled: syncEnabledInput.checked,
    syncIntervalSeconds: Math.max(
      5,
      Number.parseInt(syncIntervalInput.value, 10) || DEFAULT_SETTINGS.syncIntervalSeconds,
    ),
  };

  await chrome.storage.sync.set({ [SETTINGS_KEY]: settings });
  status.textContent = 'Settings saved.';
  setTimeout(() => {
    status.textContent = '';
  }, 2000);
}

saveBtn.addEventListener('click', async () => {
  await saveSettings();
});

openDesktop.addEventListener('click', () => {
  chrome.tabs.create({ url: 'taborganizer://open?source=extension-settings' });
});

loadSettings();
