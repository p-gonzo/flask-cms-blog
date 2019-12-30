import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to local sqlite3 file or deployed postgres instance
if os.environ['RUN_ENVIRON'] == 'sqlite3':
    APP_DIR = os.path.dirname(os.path.realpath(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(APP_DIR, 'blog.db')
elif os.environ['RUN_ENVIRON'] == 'local':
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://{user}:{pw}@{url}/{db}".format(user="postgres",pw="docker",url="localhost",db="postgres")
elif os.environ['RUN_ENVIRON'] == 'heroku':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

app.config['ADMIN_PASSWORD'] = os.environ['ADMIN_PASSWORD']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
db = SQLAlchemy(app)