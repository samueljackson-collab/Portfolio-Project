from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DashboardPage:
    URL_PATH = "/dashboard"
    WELCOME_MSG = (By.ID, "welcome-msg")
    CURRENT_USER = (By.ID, "current-user")
    NAV_PROFILE = (By.ID, "nav-profile")
    NAV_SETTINGS = (By.ID, "nav-settings")
    NAV_LOGOUT = (By.ID, "nav-logout")
    DASHBOARD_CONTENT = (By.ID, "dashboard-content")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def navigate(self):
        self.driver.get(self.base_url + self.URL_PATH)
        return self

    def get_welcome_message(self):
        try:
            return self.driver.find_element(*self.WELCOME_MSG).text
        except Exception:
            return None

    def get_current_user(self):
        try:
            return self.driver.find_element(*self.CURRENT_USER).text
        except Exception:
            return None

    def click_profile(self):
        self.driver.find_element(*self.NAV_PROFILE).click()
        return self

    def click_settings(self):
        self.driver.find_element(*self.NAV_SETTINGS).click()
        return self

    def click_logout(self):
        self.driver.find_element(*self.NAV_LOGOUT).click()
        return self

    def is_on_page(self):
        return "dashboard" in self.driver.current_url.lower() or self.driver.title == "Dashboard"

    def is_dashboard_content_visible(self):
        try:
            elem = self.driver.find_element(*self.DASHBOARD_CONTENT)
            return elem.is_displayed()
        except Exception:
            return False

    def get_nav_links(self):
        """Return dict of nav link texts and hrefs"""
        links = {}
        for name, locator in [("profile", self.NAV_PROFILE),
                               ("settings", self.NAV_SETTINGS),
                               ("logout", self.NAV_LOGOUT)]:
            try:
                elem = self.driver.find_element(*locator)
                links[name] = {"text": elem.text, "href": elem.get_attribute("href")}
            except Exception:
                links[name] = None
        return links
