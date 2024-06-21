import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from flask import current_app as app
import ssl

def get(url) -> json:
    app.logger.info(f"Reading API Get: {url}")

    try:
        _context = None
        if(url.startswith('https')):
            _context = ssl._create_unverified_context()
        with urlopen(url, context=_context) as _response:
            _data = _response.read()
            _item = json.loads(_data)
            return _item
    except HTTPError as e:
        app.logger.error(f'Error code: {e.code}')
    except URLError as e:
        app.logger.error(f'URL Error: {e.reason}')

    return {}        

