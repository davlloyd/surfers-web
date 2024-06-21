from cgitb import text
import json
import sys
import os
from sqlalchemy.sql import text
from flask import current_app as app
from main.data.models import Country, State, Region, Location, Cam
from main.data.models import db

class DataManager():

    @staticmethod
    def initDB():
        app.logger.info('DB URI: %s',app.config['SQLALCHEMY_DATABASE_URI'])
        app.logger.info('Create DB')
        _localfile = os.path.join(os.getcwd(), 'data.sqlite')
        if os.path.exists(_localfile):
            os.remove(_localfile)
        db.create_all()
        db.session.commit()
        DataManager.importData()


    @staticmethod
    def importData():
        app.logger.info('Importing data')
        try:
            with open(app.config['DATA_FILE'], 'r') as f:
                table = json.loads(f.read())
        except:
            app.logger.error(f"Error reading data import file: {app.config['DATA_FILE']}")
        else:
            for _country in table['country']:
                _cn = Country(name=_country['name'], 
                                    longitude=_country['longitude'],
                                    latitude=_country['latitude']).add()
                for _state in _country['state']:
                    _st = State(name=_state['name'],
                                        longitude=_state['longitude'],
                                        latitude=_state['latitude'], 
                                        postal=_state['postal'], 
                                        country_id=_cn).add()
                    for _region in _state['region']:
                        _re = Region(name=_region['name'], 
                                            longitude=_region['longitude'], 
                                            latitude=_region['latitude'], 
                                            state_id=_st).add()
                        for _location in _region['location']:
                            _lo = Location(name=_location['name'], 
                                                longitude=_location['longitude'], 
                                                latitude=_location['latitude'], 
                                                willy_weather=_location['willy_weather'], 
                                                willy_wind=_location['willy_wind'], 
                                                willy_tide=_location['willy_tide'], 
                                                willy_swell=_location['willy_swell'], 
                                                geohash=_location['geohash'],
                                                region_id=_re).add()
                            for _cam in _location['cam']:
                                _ca = Cam(site=_cam['site'], url=_cam['url'], location_id=_lo).add()
            app.logger.info(f"Data import completed")


    @staticmethod
    def testdb():
        try:
            db.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            app.logger.error(f'Database connection attempt failed: {str(e)}')
            return False
