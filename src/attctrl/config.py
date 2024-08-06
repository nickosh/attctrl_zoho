from decouple import config

from attctrl.logger import new_logger

logger = new_logger(__name__)


class Config:
    try:
        DEBUG = config("DEBUG", default=False, cast=bool)
        # UI_HOST = config("WEB_HOST")
        # UI_PORT = config("WEB_PORT", default=8080, cast=int)
        # UI_LISTEN = config("WEB_LISTEN", default="0.0.0.0")
        ZOHO_USERNAME = config("ZOHO_USERNAME")
        ZOHO_PASSWORD = config("ZOHO_PASSWORD")
        ZOHO_COMPANY_ID = config("ZOHO_COMPANY_ID")
        ZOHO_LOGIN_LINK = f"https://one.zoho.com/zohoone/{ZOHO_COMPANY_ID}/home/cxapp/people/"
    except Exception as e:
        logger.error(f"Fail to load app params from env: {e}")
        raise
