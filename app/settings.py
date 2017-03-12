import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ.get('DB_PORT', 3306)
DB_DBNAME = os.environ.get('DB_DBNAME', 'DropMuse')
DB_PREFIX = os.environ.get('DB_PREFIX', 'pymysql://')
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGEME')
