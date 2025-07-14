import geoip2.database
from fastapi import Request

# Download GeoLite2-Country.mmdb from MaxMind and place in project root
GEOIP_DB = "GeoLite2-Country.mmdb"
reader = geoip2.database.Reader(GEOIP_DB)

# Map country → your locale code
COUNTRY_TO_LOCALE = {
    "fr": "fr", "de": "de", "es": "es", "it": "it", "pt": "pt",
    "cn": "zh-CN", "tw": "zh-TW", "jp": "ja", "kr": "ko",
    "ru": "ru", "ar": "ar", "hi": "hi", "bn": "bn", "ur": "ur",
    # …add the rest as needed  
}

async def locale_middleware(request: Request, call_next):
    ip = request.client.host
    try:
        country = reader.country(ip).country.iso_code.lower()
        code = COUNTRY_TO_LOCALE.get(country, "en")
    except Exception:
        code = "en"
    request.state.locale = code
    response = await call_next(request)
    return response
