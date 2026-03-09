#!/usr/bin/env python3
"""
Mobile Test Automation Scaffold using Appium

This is a placeholder/scaffold for future mobile automation.
Install Appium and required dependencies before use.

Dependencies:
    pip install Appium-Python-Client selenium pytest
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest


class MobileTestBase:
    """Base class for mobile test automation."""

    @pytest.fixture(scope="function")
    def android_driver(self):
        """Setup Android driver."""
        desired_caps = {
            "platformName": "Android",
            "platformVersion": "11",
            "deviceName": "Android Emulator",
            "app": "/path/to/your/app.apk",
            "automationName": "UiAutomator2",
            "appPackage": "com.yourapp.package",
            "appActivity": ".MainActivity",
        }

        driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
        yield driver
        driver.quit()

    @pytest.fixture(scope="function")
    def ios_driver(self):
        """Setup iOS driver."""
        desired_caps = {
            "platformName": "iOS",
            "platformVersion": "14.5",
            "deviceName": "iPhone 12",
            "app": "/path/to/your/app.ipa",
            "automationName": "XCUITest",
            "bundleId": "com.yourapp.bundle",
        }

        driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
        yield driver
        driver.quit()


class TestLoginFlow(MobileTestBase):
    """Test login functionality (example)."""

    @pytest.mark.skip(reason="Scaffold - implement when ready")
    def test_login_valid_credentials(self, android_driver):
        """Test login with valid credentials."""
        driver = android_driver

        # Wait for login screen
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.yourapp:id/username"))
        )

        # Enter credentials
        username_field.send_keys("testuser")
        driver.find_element(AppiumBy.ID, "com.yourapp:id/password").send_keys(
            "testpass"
        )
        driver.find_element(AppiumBy.ID, "com.yourapp:id/loginButton").click()

        # Verify successful login
        home_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.yourapp:id/homeScreen"))
        )
        assert home_element.is_displayed()

    @pytest.mark.skip(reason="Scaffold - implement when ready")
    def test_login_invalid_credentials(self, android_driver):
        """Test login with invalid credentials."""
        driver = android_driver

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.yourapp:id/username"))
        )

        username_field.send_keys("wronguser")
        driver.find_element(AppiumBy.ID, "com.yourapp:id/password").send_keys(
            "wrongpass"
        )
        driver.find_element(AppiumBy.ID, "com.yourapp:id/loginButton").click()

        # Verify error message
        error_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.yourapp:id/errorMessage"))
        )
        assert "Invalid credentials" in error_message.text


# Page Object Model Example
class LoginPage:
    """Page Object for Login Screen."""

    def __init__(self, driver):
        self.driver = driver
        self.username_field = (AppiumBy.ID, "com.yourapp:id/username")
        self.password_field = (AppiumBy.ID, "com.yourapp:id/password")
        self.login_button = (AppiumBy.ID, "com.yourapp:id/loginButton")
        self.error_message = (AppiumBy.ID, "com.yourapp:id/errorMessage")

    def enter_username(self, username):
        """Enter username."""
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.username_field)
        )
        element.send_keys(username)

    def enter_password(self, password):
        """Enter password."""
        self.driver.find_element(*self.password_field).send_keys(password)

    def click_login(self):
        """Click login button."""
        self.driver.find_element(*self.login_button).click()

    def get_error_message(self):
        """Get error message text."""
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.error_message)
        )
        return element.text


if __name__ == "__main__":
    print("Mobile Test Automation Scaffold")
    print("=" * 50)
    print("Setup Instructions:")
    print("1. Install Appium: npm install -g appium")
    print("2. Install Python dependencies: pip install Appium-Python-Client")
    print("3. Start Appium server: appium")
    print("4. Configure your app path and capabilities")
    print("5. Run tests: pytest test_mobile.py")
    print("\nThis is a scaffold - update with your app details!")
