#!flask/bin/python
from app.application import app
import os
PORT = os.environ.get('port', 5000)
app.run(debug=True, host='0.0.0.0', port=PORT)
