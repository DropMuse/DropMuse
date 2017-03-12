import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASS = os.environ['MYSQL_PASS']
MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_DB = os.environ.get('MYSQL_DB', 'DropMuse')

SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGEME')
