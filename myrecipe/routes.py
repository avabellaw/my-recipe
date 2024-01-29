from flask import url_for, redirect, render_template, request
from myrecipe import db, app
from myrecipe.models import Users

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print("Submitted")
        return redirect(url_for("home"))
        
        
    return render_template("register.html")