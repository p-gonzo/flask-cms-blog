import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to local sqlite3 file or deployed postgres instance
if os.environ['RUN_ENVIRON'] == 'local':
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://{user}:{pw}@{url}/{db}".format(user="postgres",pw="docker",url="localhost",db="postgres")
elif os.environ['RUN_ENVIRON'] == 'heroku':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
db = SQLAlchemy(app)