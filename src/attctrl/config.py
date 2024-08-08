from pathlib import Path

from decouple import config

from attctrl.logger import new_logger

logger = new_logger(__name__)


class Config:
    try:
        DEBUG = config("DEBUG", default=False, cast=bool)
        ZOHO_USERNAME = config("ZOHO_USERNAME")
        ZOHO_PASSWORD = config("ZOHO_PASSWORD")
        ZOHO_COMPANY_ID = config("ZOHO_COMPANY_ID")
        ZOHO_LOGIN_LINK = f"https://one.zoho.com/zohoone/{ZOHO_COMPANY_ID}/home/cxapp/people/"
        GEOLOC_LAT = config("GEOLOC_LAT", default=0.0, cast=float)
        GEOLOC_LONG = config("GEOLOC_LONG", default=0.0, cast=float)

        APP_DIR = Path(__file__).resolve().parents[0]
        TEMPLATE_DIR = Path(APP_DIR, "templates")
    except Exception as e:
        logger.error(f"Fail to load app params from env: {e}")
        raise
