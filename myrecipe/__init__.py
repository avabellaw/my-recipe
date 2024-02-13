import os
from pyexpat import model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
if os.path.exists("env.py"):
    import env
    
class Base(DeclarativeBase):
  pass    

UPLOAD_FOLDER = 'image-uploads'

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(model_class=Base)

db.init_app(app)

from myrecipe import routes


