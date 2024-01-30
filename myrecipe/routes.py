from ast import Pass
from wsgiref import validate
from flask import url_for, redirect, render_template, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, login_user
from flask_bcrypt import Bcrypt
from requests import get
from myrecipe import db, app
from myrecipe.models import Users, Recipes

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
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = LoginForm()
        
    if request.method == "POST":
        user = get_user(request.form.get("username"))
        if form.validate_on_submit():
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = RegistrationForm()
    
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            encrypted_pass = bcrypt.generate_password_hash(password).decode("utf-8")
            user = Users(username=username, password=encrypted_pass) # type: ignore
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        
    return render_template("register.html", form=form)

@app.route("/my-recipes")
@login_required
def my_recipes():
    recipes = Recipes.query.filter_by(user_id=current_user.id).all()
    
    for recipe in recipes:
        # Type ignore is because the linter doesn't recognize that Users contains the field username
        recipe.created_by = Users.query.filter_by(id=recipe.user_id).first().username # type: ignore
    return render_template("my-recipes.html", recipes=recipes)

@app.route("/add-recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        ingredients = request.form.get("ingredients")
        instructions = request.form.get("instructions")
        recipe = Recipes(user_id=current_user.id, title=title, desc=desc, ingredients=ingredients, instructions=instructions) # type: ignore
        
        if validate_recipe(recipe):
            db.session.add(recipe)
            db.session.commit()
            return redirect(url_for("my_recipes"))
    return render_template("add-recipe.html")

def validate_recipe(recipe):
    return True

def get_user(username):
    return Users.query.filter_by(username=username).first()

# Wtforms


from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError  

class RegistrationForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo("password")])
    
    def validate_username(self, username):
        if get_user(username.data):
            raise ValidationError(f"Username already taken: {username.data}")
        
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=8, max=20)])
    
    def validate_username(self, username):
        if not get_user(username.data):
            raise ValidationError(f"Username does not exist: {username.data}")
        
    def validate_password(self, password):
        user = get_user(self.username.data)
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError(f"Password is incorrect.")