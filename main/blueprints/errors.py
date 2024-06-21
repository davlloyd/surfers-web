from flask import render_template
from . import bp
from main.data.models import Location

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error_description=e.description, locationnames=locationnames())

@bp.app_errorhandler(500)
def page_not_found(e):
    return render_template('500.html', error_description=e.description, locationnames=locationnames())

def locationnames():
    _request = Location.get_AllNamesSerialized()
    return _request
