from enum import Enum, unique
from flask import current_app as app

@unique
class API_URL(Enum):
    ALERTS = f"{app.config['API_URL']}/api/v1/weather/alert"
    SWELL = f"{app.config['API_URL']}/api/v1/surf/swell/"
    WATER = f"{app.config['API_URL']}/api/v1/surf/water/"
    LOCATION = f"{app.config['API_URL']}/api/v1/weather/locations/"
    WEATHER_CURRENT = f"{app.config['API_URL']}/api/v1/weather/observation/"
    HEALTHZ = f"{app.config['API_URL']}/api/v1/healthz"

    def set_location(self, locationid):
        _url = f"{self.value}{locationid}"
        return _url
