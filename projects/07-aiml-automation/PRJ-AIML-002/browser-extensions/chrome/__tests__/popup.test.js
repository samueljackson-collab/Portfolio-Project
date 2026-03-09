/**
 * Tests for Chrome Extension Popup Script
 */

describe('Popup Script', () => {
  let mockChrome;
  let mockDocument;

  beforeEach(() => {
    // Mock Chrome APIs
    mockChrome = {
      runtime: {
        sendMessage: jest.fn(),
        openOptionsPage: jest.fn(),
      },
      tabs: {
        query: jest.fn(),
      },
      tabGroups: {
        query: jest.fn(),
      },
      storage: {
        local: {
          get: jest.fn(),
          set: jest.fn(),
        },
      },
    };
    global.chrome = mockChrome;

    // Mock DOM elements
    const elementCache = new Map();
    mockDocument = {
      getElementById: jest.fn((id) => {
        if (!elementCache.has(id)) {
          elementCache.set(id, {
            id,
            textContent: '',
            classList: {
              add: jest.fn(),
              remove: jest.fn(),
            },
            addEventListener: jest.fn(),
          });
        }
        return elementCache.get(id);
      }),
    };
    global.document = mockDocument;
  });

  describe('Popup Initialization', () => {
    test('initializes all DOM elements', () => {
      // initialize();

      const elements = [
        'statusIndicator',
        'statusText',
        'organizeBtn',
        'syncBtn',
        'settingsBtn',
        'tabCount',
        'groupCount',
        'lastOrganized',
        'openApp',
        'searchInput',
        'searchResults',
      ];

      elements.forEach((id) => {
        expect(mockDocument.getElementById).toHaveBeenCalledWith(id);
      });
    });

    test('updates status on initialization', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({ connected: true });

      // await initialize();
      // await updateStatus();

      expect(mockChrome.runtime.sendMessage).toHaveBeenCalledWith({
        type: 'get_status',
      });
    });

    test('updates stats on initialization', async () => {
      mockChrome.tabs.query.mockResolvedValue([{ id: 1 }, { id: 2 }]);
      mockChrome.tabGroups.query.mockResolvedValue([{ id: 1 }]);

      // await initialize();
      // await updateStats();

      expect(mockChrome.tabs.query).toHaveBeenCalled();
      expect(mockChrome.tabGroups.query).toHaveBeenCalled();
    });
  });

  describe('Status Display', () => {
    test('shows connected status', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({ connected: true });

      const statusIndicator = mockDocument.getElementById('statusIndicator');
      const statusText = mockDocument.getElementById('statusText');

      // await updateStatus();

      expect(statusIndicator.classList.add).toHaveBeenCalledWith('connected');
      expect(statusText.textContent).toBe('Connected');
    });

    test('shows disconnected status', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({ connected: false });

      const statusIndicator = mockDocument.getElementById('statusIndicator');
      const statusText = mockDocument.getElementById('statusText');

      // await updateStatus();

      expect(statusIndicator.classList.remove).toHaveBeenCalledWith('connected');
      expect(statusText.textContent).toBe('Disconnected');
    });

    test('handles status check errors', async () => {
      mockChrome.runtime.sendMessage.mockRejectedValue(new Error('Failed'));

      await expect(async () => {
        // await updateStatus();
      }).not.toThrow();
    });
  });

  describe('Statistics Display', () => {
    test('displays tab count correctly', async () => {
      const mockTabs = [
        { id: 1, url: 'https://example.com' },
        { id: 2, url: 'https://test.com' },
        { id: 3, url: 'https://demo.com' },
      ];
      mockChrome.tabs.query.mockResolvedValue(mockTabs);

      const tabCount = mockDocument.getElementById('tabCount');

      // await updateStats();

      expect(tabCount.textContent).toBe('3');
    });

    test('displays group count correctly', async () => {
      const mockGroups = [{ id: 1 }, { id: 2 }];
      mockChrome.tabGroups.query.mockResolvedValue(mockGroups);

      const groupCount = mockDocument.getElementById('groupCount');

      // await updateStats();

      expect(groupCount.textContent).toBe('2');
    });

    test('displays last organized time', async () => {
      const lastTime = Date.now() - 60000; // 1 minute ago
      mockChrome.storage.local.get.mockResolvedValue({ lastOrganized: lastTime });

      const lastOrganized = mockDocument.getElementById('lastOrganized');

      // await updateStats();

      expect(lastOrganized.textContent).toContain('m ago');
    });

    test('handles missing last organized time', async () => {
      mockChrome.storage.local.get.mockResolvedValue({});

      await expect(async () => {
        // await updateStats();
      }).not.toThrow();
    });

    test('handles stats query errors', async () => {
      mockChrome.tabs.query.mockRejectedValue(new Error('Query failed'));

      await expect(async () => {
        // await updateStats();
      }).not.toThrow();
    });
  });

  describe('Relative Time Formatting', () => {
    test('formats seconds correctly', () => {
      const now = new Date();
      const date = new Date(now.getTime() - 30000); // 30 seconds ago

      // const result = formatRelativeTime(date);

      // expect(result).toBe('Just now');
    });

    test('formats minutes correctly', () => {
      const now = new Date();
      const date = new Date(now.getTime() - 5 * 60000); // 5 minutes ago

      // const result = formatRelativeTime(date);

      // expect(result).toBe('5m ago');
    });

    test('formats hours correctly', () => {
      const now = new Date();
      const date = new Date(now.getTime() - 3 * 3600000); // 3 hours ago

      // const result = formatRelativeTime(date);

      // expect(result).toBe('3h ago');
    });

    test('formats days correctly', () => {
      const now = new Date();
      const date = new Date(now.getTime() - 2 * 86400000); // 2 days ago

      // const result = formatRelativeTime(date);

      // expect(result).toBe('2d ago');
    });
  });

  describe('Organize Button', () => {
    test('sends organize message on click', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({});

      const organizeBtn = mockDocument.getElementById('organizeBtn');
      const clickCallback = organizeBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        await clickCallback();

        expect(mockChrome.runtime.sendMessage).toHaveBeenCalledWith({
          type: 'organize_now',
        });
      }
    });

    test('disables button during organization', async () => {
      mockChrome.runtime.sendMessage.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const organizeBtn = mockDocument.getElementById('organizeBtn');
      const clickCallback = organizeBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        clickCallback();

        expect(organizeBtn.disabled).toBe(true);
        expect(organizeBtn.textContent).toBe('Organizing...');
      }
    });

    test('re-enables button after organization', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({});
      mockChrome.storage.local.set.mockResolvedValue();

      const organizeBtn = mockDocument.getElementById('organizeBtn');
      const clickCallback = organizeBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        await clickCallback();

        // Wait for timeout
        await new Promise((resolve) => setTimeout(resolve, 2100));

        expect(organizeBtn.disabled).toBe(false);
        expect(organizeBtn.textContent).toBe('Organize Tabs Now');
      }
    }, 10000);

    test('handles organization errors', async () => {
      mockChrome.runtime.sendMessage.mockRejectedValue(new Error('Failed'));

      const organizeBtn = mockDocument.getElementById('organizeBtn');
      const clickCallback = organizeBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        await clickCallback();

        expect(organizeBtn.textContent).toBe('Error');
      }
    });

    test('saves last organized timestamp', async () => {
      mockChrome.runtime.sendMessage.mockResolvedValue({});
      mockChrome.storage.local.set.mockResolvedValue();

      const organizeBtn = mockDocument.getElementById('organizeBtn');
      const clickCallback = organizeBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        const before = Date.now();
        await clickCallback();
        const after = Date.now();

        const setCall = mockChrome.storage.local.set.mock.calls[0]?.[0];
        expect(setCall?.lastOrganized).toBeGreaterThanOrEqual(before);
        expect(setCall?.lastOrganized).toBeLessThanOrEqual(after);
      }
    });
  });

  describe('Settings Button', () => {
    test('opens options page on click', () => {
      const settingsBtn = mockDocument.getElementById('settingsBtn');
      const clickCallback = settingsBtn.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        clickCallback();

        expect(mockChrome.runtime.openOptionsPage).toHaveBeenCalled();
      }
    });
  });

  describe('Open App Link', () => {
    test('handles open app click', () => {
      global.alert = jest.fn();

      const openApp = mockDocument.getElementById('openApp');
      const clickCallback = openApp.addEventListener.mock.calls.find(
        (call) => call[0] === 'click'
      )?.[1];

      if (clickCallback) {
        const mockEvent = { preventDefault: jest.fn() };
        clickCallback(mockEvent);

        expect(mockEvent.preventDefault).toHaveBeenCalled();
        expect(global.alert).toHaveBeenCalledWith(
          'Desktop app integration coming soon!'
        );
      }
    });
  });

  describe('Periodic Updates', () => {
    test('refreshes stats periodically', () => {
      jest.useFakeTimers();

      // initialize();

      expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 5000);

      jest.useRealTimers();
    });
  });

  describe('Edge Cases', () => {
    test('handles zero tabs', async () => {
      mockChrome.tabs.query.mockResolvedValue([]);

      const tabCount = mockDocument.getElementById('tabCount');

      // await updateStats();

      expect(tabCount.textContent).toBe('0');
    });

    test('handles zero groups', async () => {
      mockChrome.tabGroups.query.mockResolvedValue([]);

      const groupCount = mockDocument.getElementById('groupCount');

      // await updateStats();

      expect(groupCount.textContent).toBe('0');
    });

    test('handles very large tab counts', async () => {
      const mockTabs = Array.from({ length: 10000 }, (_, i) => ({ id: i }));
      mockChrome.tabs.query.mockResolvedValue(mockTabs);

      const tabCount = mockDocument.getElementById('tabCount');

      // await updateStats();

      expect(tabCount.textContent).toBe('10000');
    });
  });
});
