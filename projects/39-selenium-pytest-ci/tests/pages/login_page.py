from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL_PATH = "/login"
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    ERROR_MSG = (By.ID, "error-msg")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def navigate(self):
        self.driver.get(self.base_url + self.URL_PATH)
        return self

    def login(self, username, password):
        self.driver.find_element(*self.USERNAME_INPUT).clear()
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        self.driver.find_element(*self.PASSWORD_INPUT).clear()
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()
        return self

    def get_error_message(self):
        try:
            return self.driver.find_element(*self.ERROR_MSG).text
        except:
            return None

    def is_on_page(self):
        return "login" in self.driver.current_url.lower() or self.driver.title == "Demo App - Login"
