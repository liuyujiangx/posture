from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_cors import *
app = Flask(__name__)
CORS(app, supports_credentials=True,resources=r'/*')
import os

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:1914571065lyj@localhost:3306/posture'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["SECRET_KEY"] = '235c749859ec44c2bd6064ec6da7b927'
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/")
app.debug = True
db = SQLAlchemy(app)


from app.routes import home as home_blueprint

app.register_blueprint(home_blueprint)