import json
from enum import Enum, unique
from datetime import datetime
from pickle import TRUE
from flask import render_template, request, redirect, abort
from flask import current_app as app
from . import bp
from main.data.models import Country, State, Region, Location, Cam
from main.services import web
from main.services.enums import API_URL
from main.data.utilities import DataManager


@bp.route('/', methods=["GET"])
def home():
    app.logger.info("Accessing home page")

    try:
        _alerts = web.get(API_URL.ALERTS.value)
        _message = "<b>Current Marine Weather Warnings:<b>&emsp;&emsp;&emsp;&emsp;"
        for _alert in _alerts:
            _message = _message + "<a href='" + _alert['link'] + "'>" + _alert['title'] + "</a>&emsp;&emsp;&emsp;&emsp;"
        app.logger.info("Weather Banner: {}".format(_message))
    except:
        app.logger.error("Weather Banner Generation failed")
        _message = ""


    return render_template('home.html', message=_message)

@bp.route('/beaches', methods=["GET", "POST"])
def beaches():
    app.logger.info("Accessing sites page")
    _countries = Country.query.all()
    _countryid = 0
    _states={}
    _stateid = 0
    _regions={}
    _regionid = 0
    _locations={}
    _x = "-24.971391128601727"
    _y = "135.88779862421478"
    _zoom = 2

    if request.method == "POST":
        app.logger.info("Form Post")
        _locationid = int(request.form["location"])
        if _locationid != 0:
            return redirect(f'/location/{_locationid}')
        else:
            _countryid = int(request.form["country"])
            if _countryid != 0:
                _states = State.get_ByCountry(_countryid)
                _stateid = int(request.form["state"])
                if _stateid != 0:
                    _regions = Region.get_ByState(_stateid)
                    _regionid = int(request.form["region"])
                    if _regionid != 0:
                        _locations = Location.get_ByRegion(_regionid)
                        _x = Region.query.get(_regionid).latitude
                        _y = Region.query.get(_regionid).longitude
                    else:
                        _x = State.query.get(_stateid).latitude
                        _y = State.query.get(_stateid).longitude
                else:
                    _x = Country.query.get(_countryid).latitude
                    _y = Country.query.get(_countryid).longitude
    else:
        # added logic to default to Australia if first access
        _countryid = 1
        _states = State.get_ByCountry(_countryid)
        _x = Country.query.get(_countryid).latitude
        _y = Country.query.get(_countryid).longitude

    return render_template('beaches.html', countries=_countries, countryid=_countryid,
                                        states=_states, stateid=_stateid,
                                        regions=_regions, regionid=_regionid,
                                        locations=_locations, x=_x, y=_y)


@bp.route('/location/<locationid>', methods=["GET"])
def location(locationid):
    app.logger.info(f"Accessing Location page for locationid {locationid}")
    _swell={}
    _water={}
    _weather={}
    _cams={}

    if locationid != 0:
        _location = Location.get_ById(locationid)
        _locations = Location.get_ByRegion(_location.region_id)
        _cams = Cam.get(locationid)
        # Need the Geohash tag for getting data from BOM API (ref https://en.wikipedia.org/wiki/Geohash)
        if not _location.geohash:
            # use BOM location search query to get geohash. Need both location name and state to ensure correct location
            _state = Location.get_LocationState(locationid)
            _searchstring = f'{_location.name}+{_state}'.replace(' ', '+')

            _result = web.get(API_URL.LOCATION.set_location(_searchstring))
            if len(_result) > 0:
                # Update record with geohash value
                _location.geohash = _result[0]['geohash']
                Location.update_LocationGeohash(locationid, _location.geohash)

        _apiresults = False
        if len(web.get(API_URL.HEALTHZ.value)) > 0:
            # Query current conditions from API Service if geohash value present
            if _location.geohash:
                _swell = web.get(API_URL.SWELL.set_location(_location.geohash))
                _water = web.get(API_URL.WATER.set_location(_location.geohash))
                _weather = web.get(API_URL.WEATHER_CURRENT.set_location(_location.geohash))
                _apiresults = True

        return render_template('location.html', locationid=locationid, location=_location, 
                                                locations=_locations, cams=_cams, 
                                                swell=_swell, water=_water,weather=_weather,
                                                apiresults=_apiresults) 
    else:
        abort(404)


@bp.route('/forum', methods=["GET", "POST"])
def forum():
    app.logger.info("Accessing Forum page")
    return render_template('forum.html')

@bp.route('/about', methods=["GET"])
def about():
    app.logger.info("Accessing About page")


    _health = health()
    if _health is not None:
        if _health['health'] == 'ok':
            _service_health = '&#10004;'
        else:
            _service_health = '&#9747;'
        if _health['api'] == 'ok':
            _api_health = '&#10004;'
        else:
            _api_health = '&#9747;'
        if _health['database'] == 'ok':
            _database_health = '&#10004;'
        else:
            _database_health = '&#9747;'
    else:
        _service_health = '?'
        _api_health = '?'
        _database_health = '?'

    return render_template('about.html', service_health=_service_health,
                                        api_health=_api_health,
                                        database_health=_database_health)


@bp.route('/search/<location>', methods=["GET"])
def search(location):
    app.logger.info(f"Search requested - {location}")
    if "," in location:
        _entries = location.split(',')
        _town = _entries[0].strip()
        _state = _entries[1].strip()
        _results = Location.find(_town, _state)
    else:
        _results = Location.find(location.strip())
    
    for item in json.loads(_results):
        _url = '/location/{}'.format(item['id'])
    return redirect(_url)

"""
Heath status check routine
"""
@bp.route('/healthz', methods=["GET"])
def health():
    app.logger.info("Getting service health status")
    _status = web.get(API_URL.HEALTHZ.value)
    if len(_status) > 0:
        _api = _status['health']
    else:
        _api = 'fail'
    if DataManager.testdb():
        _database = 'ok'
    else:
        _database= 'fail'

    if ':' in app.config['SQLALCHEMY_DATABASE_URI']:
        _database_type = app.config['SQLALCHEMY_DATABASE_URI'].split(':')[0]
    else:
        _database_type = "not set"

    _status = {
        "health": "ok",
        "environment": app.config['ENV'],
        "database": _database,
        "database_type": _database_type,
        "api": _api,
        "api_url": API_URL.HEALTHZ.value
    }
    return _status


## Jinja Variables
@bp.context_processor
def inject_locationnames():
    _response = Location.get_AllNamesSerialized()
    return dict(locationnames=_response)

## Jinja Functions 
@bp.context_processor
def utilities():
    def item_count(list):
        return len(list)

    def camlist(locationid):
        _cams = {}
        if locationid != 0:
            _cams = Cam.get(locationid)
        return _cams

    def getvideoid(id):
        return 'video-{0}'.format(id)

    def getwgsite(locationid):
        _location = Location.get_id(locationid)
        return _location.wg_site

    def rowstart(entry):
        if entry%2 == 0:
            return f'<td style="border:none;">'
        else:
            return f'<tr><td style="border:none;">'

    def rowend(entry):
        if entry%2 == 0:
            return f'</td></tr>'
        else:
            return f'</td>'

    def locationsbyregion_asdict(regionid):
        _response = Location.get_ByRegionSerialized(regionid)
        return _response

    def locationsbycountry_asdict(countryid):
        _response = Location.get_ByCountrySerialized(countryid)
        return _response

    def locationsbystate_asdict(stateid):
        _response = Location.get_ByStateSerialized(stateid)
        return _response


    return dict(camlist=camlist, 
                item_count=item_count, 
                getvideoid=getvideoid, 
                getwgsite=getwgsite, 
                rowstart=rowstart, 
                rowend=rowend, 
                locationsbyregion_asdict=locationsbyregion_asdict, 
                locationsbycountry_asdict=locationsbycountry_asdict,
                locationsbystate_asdict=locationsbystate_asdict)
