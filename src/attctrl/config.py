from pathlib import Path

from decouple import config

from attctrl.logger import new_logger

logger = new_logger(__name__)


class Config:
    try:
        DEBUG = config("DEBUG", default=False, cast=bool)
        GLITCHTIP_DNS = config("GLITCHTIP_DNS", default="")
        ZOHO_USERNAME = config("ZOHO_USERNAME")
        ZOHO_PASSWORD = config("ZOHO_PASSWORD")
        ZOHO_COMPANY_ID = config("ZOHO_COMPANY_ID")
        ZOHO_LOGIN_LINK = f"https://one.zoho.com/zohoone/{ZOHO_COMPANY_ID}/home/cxapp/people/"
        GEOLOC_LAT = config("GEOLOC_LAT", default=0.0, cast=float)
        GEOLOC_LONG = config("GEOLOC_LONG", default=0.0, cast=float)

        APP_DIR = Path(__file__).resolve().parents[0]
        TEMPLATE_DIR = Path(APP_DIR, "templates")
        STATIC_DIR = Path(APP_DIR, "static")
        ROOT_DIR = Path(__file__).resolve().parents[2]
        DATA_DIR = Path(ROOT_DIR, "data")
        DATA_DIR.mkdir(exist_ok=True)
    except Exception as e:
        logger.error(f"Fail to load app params from env: {e}")
        raise
