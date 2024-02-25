"""
Contains the intialization code for My Recipe.

Intializes the Flask app and the database connection.

Handles the configuration of the app.

Imports routes.
"""

import os
from enum import Enum
from pyexpat import model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

if os.path.exists("env.py"):
    import env

PACKAGE_NAME = "myrecipe"
UPLOAD_FOLDER = "image-uploads"

DIETARY_TAGS = ["vv", "v", "gf", "df", "nf", "ef"]

# Flask configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if os.environ.get("DEVELOPMENT") == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
else:
    URI = str(os.environ.get("DATABASE_URL"))
    if URI.startswith("postgres://"):
        URI = URI.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = URI
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PACKAGE_NAME'] = PACKAGE_NAME

has_cloudinary_creds = os.environ.get("cloud_name") is not None and os.environ.get(
    "api_key") is not None and os.environ.get("api_secret") is not None

app.config['SAVE_IMAGES_LOCALLY'] = not has_cloudinary_creds


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    __abstract__ = True


db = SQLAlchemy(model_class=Base)

db.init_app(app)

class UserType(Enum):
    """
    Enumeration for user types.

    Attributes:
        STANDARD (str): Standard user type.
        ADMIN (str): Admin user type.
    """
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"

from myrecipe import routes
