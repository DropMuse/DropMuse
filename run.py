#!flask/bin/python
from app.application import app
from app.settings import SERVER_ENV, PORT
DEBUG = SERVER_ENV == 'dev'
app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
