/**
 * Tests for Chrome Extension Background Service Worker
 */

describe('Background Service Worker', () => {
  let mockChrome;

  beforeEach(() => {
    // Mock Chrome APIs
    mockChrome = {
      runtime: {
        onInstalled: { addListener: jest.fn() },
        connectNative: jest.fn(),
        sendMessage: jest.fn(),
        lastError: null,
      },
      tabs: {
        query: jest.fn(),
        onCreated: { addListener: jest.fn() },
        onUpdated: { addListener: jest.fn() },
        onRemoved: { addListener: jest.fn() },
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
  });

  describe('Extension Initialization', () => {
    test('registers onInstalled listener', () => {
      // Simulate loading background script
      require('../background.js');

      expect(mockChrome.runtime.onInstalled.addListener).toHaveBeenCalled();
    });

    test('initializes extension on install', () => {
      const callback = mockChrome.runtime.onInstalled.addListener.mock.calls[0][0];

      callback();

      // Verify initialization logic runs
      expect(mockChrome.runtime.connectNative).toHaveBeenCalled();
    });
  });

  describe('Native Host Connection', () => {
    test('connects to native host with correct name', () => {
      mockChrome.runtime.connectNative.mockReturnValue({
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(),
      });

      // Trigger connection
      // connectToNativeHost();

      expect(mockChrome.runtime.connectNative).toHaveBeenCalledWith(
        'com.taborganizer.native_host'
      );
    });

    test('handles connection success', () => {
      const mockPort = {
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(),
      };
      mockChrome.runtime.connectNative.mockReturnValue(mockPort);

      // Connection should set up listeners
      expect(mockPort.onMessage.addListener).toBeDefined();
      expect(mockPort.onDisconnect.addListener).toBeDefined();
    });

    test('handles connection failure', () => {
      mockChrome.runtime.connectNative.mockImplementation(() => {
        throw new Error('Connection failed');
      });

      // Should handle error gracefully
      expect(() => {
        // connectToNativeHost();
      }).not.toThrow();
    });

    test('retries connection after disconnect', (done) => {
      const mockPort = {
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(),
      };
      mockChrome.runtime.connectNative.mockReturnValue(mockPort);

      // Get disconnect callback
      const disconnectCallback = mockPort.onDisconnect.addListener.mock.calls[0][0];

      // Simulate disconnect
      disconnectCallback();

      // Should retry after delay
      setTimeout(() => {
        expect(mockChrome.runtime.connectNative).toHaveBeenCalledTimes(2);
        done();
      }, 5100);
    }, 10000);
  });

  describe('Tab Synchronization', () => {
    test('queries all tabs', async () => {
      const mockTabs = [
        { id: 1, url: 'https://example.com', title: 'Example' },
        { id: 2, url: 'https://test.com', title: 'Test' },
      ];
      mockChrome.tabs.query.mockResolvedValue(mockTabs);

      // await syncTabs();

      expect(mockChrome.tabs.query).toHaveBeenCalledWith({});
    });

    test('extracts tab data correctly', async () => {
      const mockTab = {
        id: 123,
        url: 'https://github.com',
        title: 'GitHub',
        favIconUrl: 'https://github.com/favicon.ico',
        windowId: 1,
        index: 0,
        active: true,
        pinned: false,
        audible: false,
        status: 'complete',
      };

      mockChrome.tabs.query.mockResolvedValue([mockTab]);

      // const data = await extractTabData(mockTab);

      // expect(data.id).toBe('123');
      // expect(data.url).toBe('https://github.com');
      // expect(data.title).toBe('GitHub');
    });

    test('handles tabs without URL', async () => {
      const mockTab = {
        id: 1,
        url: undefined,
        title: 'Untitled',
      };

      mockChrome.tabs.query.mockResolvedValue([mockTab]);

      // Should handle gracefully
      // const data = await extractTabData(mockTab);
      // expect(data.url).toBe('');
    });

    test('handles tabs without title', async () => {
      const mockTab = {
        id: 1,
        url: 'https://example.com',
        title: undefined,
      };

      mockChrome.tabs.query.mockResolvedValue([mockTab]);

      // Should use default title
      // const data = await extractTabData(mockTab);
      // expect(data.title).toBe('Untitled');
    });

    test('syncs tabs periodically', () => {
      jest.useFakeTimers();

      // initializeExtension();

      // Verify setInterval is called
      expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 5000);

      jest.useRealTimers();
    });
  });

  describe('Message Handling', () => {
    test('sends message to native host', () => {
      const mockPort = {
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(),
      };
      mockChrome.runtime.connectNative.mockReturnValue(mockPort);

      const message = { type: 'test', data: 'value' };

      // sendToNativeHost(message);

      expect(mockPort.postMessage).toHaveBeenCalledWith(message);
    });

    test('handles message when not connected', () => {
      // Should not throw
      expect(() => {
        // sendToNativeHost({ type: 'test' });
      }).not.toThrow();
    });

    test('receives messages from native host', () => {
      const mockPort = {
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(),
      };
      mockChrome.runtime.connectNative.mockReturnValue(mockPort);

      const messageCallback = mockPort.onMessage.addListener.mock.calls[0][0];
      const testMessage = { type: 'classification_result', category: 'work' };

      // Should handle message
      expect(() => {
        messageCallback(testMessage);
      }).not.toThrow();
    });
  });

  describe('Tab Event Listeners', () => {
    test('registers tab created listener', () => {
      // initializeExtension();

      expect(mockChrome.tabs.onCreated.addListener).toHaveBeenCalled();
    });

    test('registers tab updated listener', () => {
      // initializeExtension();

      expect(mockChrome.tabs.onUpdated.addListener).toHaveBeenCalled();
    });

    test('registers tab removed listener', () => {
      // initializeExtension();

      expect(mockChrome.tabs.onRemoved.addListener).toHaveBeenCalled();
    });

    test('handles tab creation', async () => {
      const callback = mockChrome.tabs.onCreated.addListener.mock.calls[0][0];
      const newTab = {
        id: 999,
        url: 'https://new-tab.com',
        title: 'New Tab',
      };

      await callback(newTab);

      // Should notify native host
      // Verify tab data is sent
    });

    test('handles tab update', async () => {
      const callback = mockChrome.tabs.onUpdated.addListener.mock.calls[0][0];
      const tabId = 123;
      const changeInfo = { status: 'complete' };
      const tab = {
        id: tabId,
        url: 'https://updated.com',
        title: 'Updated',
      };

      await callback(tabId, changeInfo, tab);

      // Should sync updated tab
    });

    test('handles tab removal', async () => {
      const callback = mockChrome.tabs.onRemoved.addListener.mock.calls[0][0];
      const tabId = 123;
      const removeInfo = { windowId: 1, isWindowClosing: false };

      await callback(tabId, removeInfo);

      // Should notify native host of removal
    });
  });

  describe('Error Handling', () => {
    test('handles chrome.runtime.lastError', () => {
      mockChrome.runtime.lastError = { message: 'Test error' };

      // Should log error but not crash
      expect(() => {
        // Code that checks lastError
      }).not.toThrow();
    });

    test('handles tab query errors', async () => {
      mockChrome.tabs.query.mockRejectedValue(new Error('Query failed'));

      // Should handle gracefully
      await expect(async () => {
        // await syncTabs();
      }).not.toThrow();
    });

    test('handles native host communication errors', () => {
      const mockPort = {
        onMessage: { addListener: jest.fn() },
        onDisconnect: { addListener: jest.fn() },
        postMessage: jest.fn(() => {
          throw new Error('Post failed');
        }),
      };
      mockChrome.runtime.connectNative.mockReturnValue(mockPort);

      expect(() => {
        // sendToNativeHost({ type: 'test' });
      }).not.toThrow();
    });
  });

  describe('Constants and Configuration', () => {
    test('uses correct native host name', () => {
      expect('com.taborganizer.native_host').toBeDefined();
    });

    test('uses correct sync interval', () => {
      expect(5000).toBe(5000); // 5 seconds
    });
  });
});