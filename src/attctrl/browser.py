from playwright.sync_api import sync_playwright

from attctrl.config import Config


class LoginPageSelectors:
    username_input = "input[placeholder='Email address or mobile number']"
    password_input = "input[placeholder='Enter password']"
    next_button = "button:has-text('Next')"


class DashboardPageSelectors:
    url = "**/dashboard"


class BrowserControl:
    def __init__(self, url: str = Config.ZOHO_LOGIN_LINK) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=not Config.DEBUG)
        self.page = self.browser.new_page()
        self.page.goto(url)

    def teardown(self):
        self.browser.close()
        self.playwright.stop()

    def __del__(self):
        self.teardown()

    def login(self, username: str = Config.ZOHO_USERNAME, password: str = Config.ZOHO_PASSWORD):
        self.page.fill(LoginPageSelectors.username_input, username)
        self.page.click(LoginPageSelectors.next_button)
        self.page.fill(LoginPageSelectors.username_input, password)
        self.page.click(LoginPageSelectors.next_button)
        self.page.wait_for_url(DashboardPageSelectors.url)
