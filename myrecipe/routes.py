from flask import url_for, redirect, render_template, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, login_user
from flask_bcrypt import Bcrypt
from requests import get
from myrecipe import db, app
from myrecipe.models import Users

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user(request.form.get("username"))
        if validate_login(user, request.form.get("password")):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        encrypted_pass = bcrypt.generate_password_hash(password).decode("utf-8")
        user = Users(username=username, password=encrypted_pass) # type: ignore
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
        
        
    return render_template("register.html")

def get_user(username):
    return Users.query.filter_by(username=username).first()

def validate_login(user, password):
    if user and bcrypt.check_password_hash(user.password, password):
        return True
    return False