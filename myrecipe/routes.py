from flask import url_for, redirect, render_template
from myrecipe import db, app

@app.route("/")
def home():
    return "helloworld"