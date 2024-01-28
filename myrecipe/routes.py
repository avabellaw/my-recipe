from flask import url_for, redirect, render_template
from myrecipe import db, app
# from myrecipe.models import 

@app.route("/")
def home():
    return render_template("index.html")