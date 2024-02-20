import os
from pyexpat import model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
if os.path.exists("env.py"):
    import env
    
class Base(DeclarativeBase):
  pass    

PACKAGE_NAME = "myrecipe"
UPLOAD_FOLDER = "image-uploads"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if os.environ.get("DEVELOPMENT") == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
else:
    uri = str(os.environ.get("DATABASE_URL"))
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PACKAGE_NAME'] = PACKAGE_NAME

has_aws_creds = os.environ.get("CLOUDCUBE_ACCESS_KEY_ID") != None and os.environ.get("CLOUDCUBE_SECRET_ACCESS_KEY") != None and os.environ.get("CLOUDCUBE_URL") != None

app.config['SAVE_IMAGES_LOCALLY'] = not has_aws_creds

db = SQLAlchemy(model_class=Base)

db.init_app(app)

from myrecipe import routes