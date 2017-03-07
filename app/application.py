from flask import Flask, render_template
import pymysql
from settings import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB

app = Flask(__name__)

conn = pymysql.connect(host=MYSQL_HOST,
                       user=MYSQL_USER,
                       password=MYSQL_PASS,
                       port=MYSQL_PORT,
                       db=MYSQL_DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def hello_world():
    return render_template('index.html')
