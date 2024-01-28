import os
from pyexpat import model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
if os.path.exists("env.py"):
    import env
    
class Base(DeclarativeBase):
  pass    

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

db = SQLAlchemy(model_class=Base)

from myrecipe import routes


