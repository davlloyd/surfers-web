import os
import json
from pyservicebinding import binding

basedir = os.getcwd()

class Config:
    VERSION = '17'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'
    SESSION_COOKIE_HTTPONLY = False
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    ENV = 'unset'
    USER_PORT = os.environ.get('USER_PORT') or "8080"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('DB_TRACK_MODIFICATIONS') or False
    DATA_FILE = os.environ.get('DATA_FILE') or f'{basedir}/main/data/data.json'
    API_URL = os.environ.get('API_URL') or "https://surfersapi.alpha/api/v1"

    if 'VCAP_SERVICES' in os.environ:
        _vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        _mysql_srv = _vcap_services['p.mysql'][0]
        _cred = _mysql_srv['credentials']
        if _cred:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_cred['username']}:{_cred['password']}@{_cred['hostname']}:{_cred['port']}/{_cred['name']}"
        else:
            print("VCAP_SERVICES present but no db binding detected")
    else:
        try:
            _sb = binding.ServiceBinding()
            _db = _sb.bindings('mysql')
        except binding.ServiceBindingRootMissingError:
            print("Environment Variable SERVICE_BINDING_ROOT not set")
        else:
            if _db:
                SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_db[0]['username']}:{_db[0]['password']}@{_db[0]['host']}:{_db[0]['port']}/{_db[0]['database']}"
                print(f'Binding DB URI: {SQLALCHEMY_DATABASE_URI}')
            else:
                print('MySQL Binding not found, reverting to sqlite local store')

            _api = _sb.bindings('api')
            if _api:
                API_URL = _api[0]['url']
            else:
                print('API Binding not found, reverting to environment variables or defaults')


    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    ENV = 'production'
    if Config.SQLALCHEMY_DATABASE_URI is None:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:user@192.168.0.10/surferslookout'    

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    if Config.SQLALCHEMY_DATABASE_URI is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

class TestingConfig(Config):
    TESTING = True
    ENV = 'testing'
    if Config.SQLALCHEMY_DATABASE_URI is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite://'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
