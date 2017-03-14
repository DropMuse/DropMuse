import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', 3306)
DB_DBNAME = os.environ.get('DB_DBNAME', 'DropMuse')
DB_PREFIX = os.environ.get('DB_PREFIX', 'mysql+pymysql://')
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGEME')

conn_str = "{}{}:{}@{}:{}/{}".format(DB_PREFIX,
                                     DB_USER,
                                     DB_PASS,
                                     DB_HOST,
                                     DB_PORT,
                                     DB_DBNAME)

# Override with Heroku configuration if available
DB_URL = os.environ.get('DATABASE_URL', conn_str)
DB_URL = os.environ.get('CLEARDB_DATABASE_URL', DB_URL)

if DB_URL.startswith('mysql://'):
    DB_URL = 'mysql+pymyql:' + DB_URL.split(':')[0]
