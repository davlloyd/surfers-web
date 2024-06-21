from cgitb import text
import json
from datetime import datetime
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

## Table that stores regional data
class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)

    def __init__(self, name: str, latitude: str, longitude: str):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.id = self.add()

    def __repr__(self):
        return f'<Country: {self.name}>'

    def add(self) -> int:
        _id = None
        db.session.add(self)
        try:
            db.session.commit()
            app.logger.info('Country Record Added: %s', self.name)
        except IntegrityError:
            db.session.rollback()

        if self.id is None:
            _resp = Country.query.with_entities(Country.id).filter(Country.name == self.name).first()
            _id = _resp.id
        else:
            _id = self.id

        return _id


## Table that stores regional data
class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    postal = db.Column(db.String(16), unique=True, index=True)
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))

    def __init__(self, name: str, postal: str, latitude: str, longitude: str, country_id: int):
        self.name = name
        self.postal = postal
        self.latitude = latitude
        self.longitude = longitude
        self.country_id = country_id
        self.id = self.add()

    def __repr__(self):
        return f'<State: {self.name}>'

    def add(self) -> int:
        _id = None
        db.session.add(self)
        try:
            db.session.commit()
            app.logger.info('State Record Added: %s', self.name)
        except IntegrityError:
            db.session.rollback()

        if self.id is None:
            _resp = State.query.with_entities(State.id).filter(State.name == self.name).first()
            _id = _resp.id
        else:
            _id = self.id

        return _id

    @staticmethod
    def get_ByCountry(countryid):
        _request = State.query.filter(State.country_id == countryid).all()
        return _request



## Table that stores regional data
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))

    def __init__(self, name: str, latitude: str, longitude: str, state_id: int):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.state_id = state_id
        self.id = self.add()

    def __repr__(self):
        return f'<Region: {self.name}>'

    def add(self) -> int:
        _id = None
        db.session.add(self)
        try:
            db.session.commit()
            app.logger.info('Region Record Added: %s', self.name)
        except IntegrityError:
            db.session.rollback()

        if self.id is None:
            _resp = Region.query.with_entities(Region.id).filter(Region.name == self.name).first()
            _id = _resp.id
        else:
            _id = self.id

        return _id

    @staticmethod
    def get_ById(regionid):
        _resp = Region.query.filter(Region.id == regionid).first()
        return _resp

    @staticmethod
    def get_ByState(stateid):
        _request = Region.query.filter(Region.state_id == stateid).all()
        return _request


## Table that stores or general location information
class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, index=True)
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    willy_weather = db.Column(db.Text)
    willy_wind = db.Column(db.Text)
    willy_tide = db.Column(db.Text)
    willy_swell = db.Column(db.Text)
    geohash = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    __table_args__ = (
        db.UniqueConstraint('name', 'region_id'),
    )

    def __init__(self, name: str, willy_weather: str, willy_wind: str, 
                willy_tide: str, willy_swell: str, geohash: str,
                latitude: str, longitude: str, region_id: int):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.willy_weather = willy_weather
        self.willy_tide = willy_tide
        self.willy_wind = willy_wind
        self.willy_swell = willy_swell
        self.geohash = geohash
        self.region_id = region_id
        self.id = self.add()

    def __repr__(self):
        return f'<Location: {self.name}>'


    def add(self) -> int:
        _id = None
        db.session.add(self)
        try:
            db.session.commit()
            app.logger.info(f'Location Record Added: {self.name}')
        except IntegrityError:
            db.session.rollback()

        if self.id is None:
            _resp = Location.query.with_entities(Location.id).filter(Location.name == self.name).first()
            _id = _resp.id
        else:
            _id = self.id

        return _id

    def get_id(self) -> int:
        _resp = Location.query.with_entities(Location.id).filter(Location.name == self.name).first()
        if(_resp is None):
            _id = self.add()
        else:
            _id = _resp.id
        return _id

    @staticmethod
    def find(location, state='%'):
        _loccon = '{}%'.format(location) 
        _resp = db.session.query(Location, Region, State).filter(
                                                            State.id==Region.state_id, 
                                                            Region.id==Location.region_id,
                                                            Location.name.like(_loccon),
                                                            State.postal.like(state)).all()
        _json = []
        for _row in _resp:
            _json.append({'name': _row.Location.name,
                        'id': _row.Location.id,
                        'state': _row.State.name
                        })

        return json.dumps(_json)


    @staticmethod
    def get_ById(locationid):
        _resp = Location.query.filter(Location.id == locationid).first()
        return _resp

    @staticmethod
    def get_ByRegion(regionid):
        _request = Location.query.filter(Location.region_id == regionid).order_by(Location.name.asc()).all()
        return _request

    @staticmethod
    def get_AllNamesSerialized():
        _resp = db.session.query(Location, Region, State).filter(
                                        State.id==Region.state_id, 
                                        Region.id==Location.region_id).all()
        _json = []
        for _row in _resp:
            _json.append({'name': _row.Location.name,
                        'postal': _row.State.postal
                        })

        return json.dumps(_json)

    @staticmethod
    def get_ByRegionSerialized(regionid):
        _request = Location.query.filter(Location.region_id == regionid).order_by(Location.name.asc()).all()
        _json = []
        for _row in _request:
            _json.append({'name': _row.name,
                          'latitude': _row.latitude,
                          'longitude': _row.longitude,
                          'id': _row.id
                          })

        return json.dumps(_json)
    
    @staticmethod
    def get_ByCountrySerialized(countryid):
        _resp = db.session.query(Location, Region, State, Country).filter(
                                                            Country.id==State.country_id, 
                                                            State.id==Region.state_id, 
                                                            Region.id==Location.region_id,
                                                            Country.id==countryid).all()
        _json = []
        for _row in _resp:
            _json.append({'name': _row.Location.name,
                          'latitude': _row.Location.latitude,
                          'longitude': _row.Location.longitude,
                          'id': _row.Location.id
                          })
        return json.dumps(_json)
        
    
    @staticmethod
    def get_ByStateSerialized(stateid):
        _resp = db.session.query(Location, Region, State).filter(
                                                            State.id==Region.state_id, 
                                                            Region.id==Location.region_id,
                                                            State.id==stateid).all()
        _json = []
        for _row in _resp:
            _json.append({'name': _row.Location.name,
                          'latitude': _row.Location.latitude,
                          'longitude': _row.Location.longitude,
                          'id': _row.Location.id
                          })
        return json.dumps(_json)

    @staticmethod
    def get_LocationState(locationid):
        _resp = db.session.query(Location, Region, State).filter(
                                                            State.id==Region.state_id, 
                                                            Region.id==Location.region_id,
                                                            Location.id==locationid).first()
        if _resp:
            return _resp.State.postal
        else:
            return None

    # Update the geohash value in the location entry specified
    @staticmethod
    def update_LocationGeohash(locationid, geohash):
        _stmt = update(Location).where(Location.id == locationid).values(
                                    geohash=geohash).execution_options(synchronize_session="fetch")
        _result = db.session.execute(_stmt)
        try:
            db.session.commit()
            app.logger.info(f'Location record updated: {locationid}')
        except IntegrityError:
            db.session.rollback()        
        return _result.rowcount


## Class that stores all camera installations, Locations can have 1 or more cameras
class Cam(db.Model):
    __tablename__ = 'cam'
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(64), unique=False, index=True)
    url = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    __table_args__ = (
        db.UniqueConstraint('site', 'location_id'),
    )

    def __repr__(self):
        return f'<Cam: {self.site}>'


    def __init__(self, site: str, url: str, location_id: int):
        self.site = site
        self.url = url
        self.location_id = location_id
        self.id = self.add()


    def add(self) -> int:
        _id = None
        db.session.add(self)
        try:
            db.session.commit()
            app.logger.info('Cam Record Added: %s', self.site)
        except IntegrityError:
            db.session.rollback()

        if self.id is None:
            _resp = Cam.query.with_entities(Cam.id).filter(Cam.site == self.site, Cam.location_id == self.location_id).first()
            _id = _resp.id
        else:
            _id = self.id

        return _id


    def get(locationid):
        _request = Cam.query.filter(Cam.location_id == locationid).all()
        return _request

