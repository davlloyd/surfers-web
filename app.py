import os
from main import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialise application context
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
	app.run(debug=app.config['DEBUG'],host='0.0.0.0', port=app.config['USER_PORT'])

