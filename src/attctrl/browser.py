from playwright.sync_api import Page, expect, sync_playwright

from attctrl.config import Config
from attctrl.logger import new_logger

logger = new_logger(__name__, log_file="debug.log")


class BasicPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def __call__(self) -> Page:
        return self.page


class LoginPage(BasicPage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.locator("input[placeholder='Email address or mobile number']")
        self.password_input = page.locator("input[placeholder='Enter password']")
        self.next_button = page.locator("button#nextbtn:has-text('Next')")
        self.understand_button = page.locator("button#continue_button:has-text('I Understand')")
        self.daily_limit = page.locator("text=You've reached your daily sign-in limit.")

    def is_daily_limit_warning(self) -> bool:
        try:
            expect(self.understand_button).to_be_visible()
            return True
        except Exception:
            return False

    def is_daily_limit_reached(self) -> bool:
        try:
            expect(self.daily_limit).to_be_visible()
            return True
        except Exception:
            return False


class DashboardPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.url = "**/dashboard"
        self.iframe = "iframe#peopleLoadFrame"
        self.atte_header = "h3.dash-title[title='Attendance']"
        self.time_span = "span#ZPAtt_Dash_CurrTime"
        self.att_button = self.page.frame_locator(self.iframe).locator("button.out.chlodIng")

    def wait_for_loading(self):
        self.page.wait_for_url(self.url)


class BrowserControl:
    def __init__(self, url: str = Config.ZOHO_LOGIN_LINK) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=not Config.DEBUG)
        self.context = self.browser.new_context()
        self.page = self.browser.new_page()
        self.login_pg = LoginPage(self.page)
        self.dashboard_pg = DashboardPage(self.page)

        self.page.goto(url)

    def teardown(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def __del__(self):
        self.teardown()

    def login(self, username: str = Config.ZOHO_USERNAME, password: str = Config.ZOHO_PASSWORD):
        self.login_pg.username_input.fill(username)
        self.login_pg.next_button.click()
        if self.login_pg.is_daily_limit_reached():
            # NOTE: Zoho have daily limit in 20 login events.
            msg = "Daily sign-in limit reached. Breaking the task."
            logger.exception(msg)
            raise EnvironmentError(msg)
        self.login_pg.password_input.fill(password)
        self.login_pg.next_button.click()
        if self.login_pg.is_daily_limit_warning():
            self.login_pg.understand_button.click()
        self.dashboard_pg.wait_for_loading()
        self.dashboard_pg.att_button.wait_for(state="visible")

    def switch_attendancy(self):
        logger.debug(self.context.cookies())
        self.dashboard_pg.att_button.click()
        self.context.grant_permissions(["geolocation"])

    def get_att_state(self):
        return self.dashboard_pg.att_button.inner_text()


bc = BrowserControl()
bc.login()
print(bc.get_att_state())
bc.switch_attendancy()
