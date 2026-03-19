import pytest
import threading
from app.app import app as flask_app

@pytest.fixture(scope="session")
def live_server():
    """Start Flask app in background thread for Selenium tests"""
    def run():
        flask_app.run(port=5002, debug=False, use_reloader=False)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    import time
    time.sleep(1)  # Wait for server to start
    yield "http://localhost:5002"

@pytest.fixture
def driver():
    """Selenium WebDriver with headless Chrome"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()
