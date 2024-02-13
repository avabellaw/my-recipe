import os
from flask import url_for, redirect, render_template, request, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, login_user
from flask_bcrypt import Bcrypt
from myrecipe import db, app
from myrecipe.models import Users, Recipes

# WTForms imports
from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Homepage
@app.route("/")
def home():
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    return render_template("index.html", recipes=recipes)

# Login user
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

# Register user
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

# My recipies
@app.route("/my-recipes")
@login_required
def my_recipes():
    recipes = Recipes.query.filter_by(user_id=current_user.id).all()
    
    add_created_by_to_recipes(recipes)
    return render_template("my-recipes.html", recipes=recipes)

# View recipe
@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def view_recipe(recipe_id):
    recipe = Recipes.query.get(recipe_id)
    recipe.created_by = Users.query.filter_by(id=recipe.user_id).first().username # type: ignore
    return render_template("view-recipe.html", recipe=recipe)

# Add recipe
@app.route("/add-recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    form = AddRecipeForm()
    
    if request.method == "POST":
        title = form.title.data
        desc = form.desc.data 
        ingredients = form.ingredients.data
        instructions = form.instructions.data
        if form.validate_on_submit():
            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            image_url_parts = app.config['UPLOAD_FOLDER'].split("/")[1:] # Remove "myrecipe" from the path
            image_url = "/" + "/".join(image_url_parts) + "/" + filename 
            
            recipe = Recipes(user_id=current_user.id, title=title, desc=desc, ingredients=ingredients, instructions=instructions, image_url=image_url) # type: ignore
        
            db.session.add(recipe)
            db.session.commit()
            return redirect(url_for("my_recipes"))
    return render_template("add-recipe.html", form=form)

# From Flask documentation
@app.route('/image-uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    
# Helpers
def get_user(username):
    return Users.query.filter_by(username=username).first()

def get_all_recipes():
    return Recipes.query.all()

def add_created_by_to_recipes(recipes):
     for recipe in recipes:
        # Type ignore is because the linter doesn't recognize that Users contains the field username
        recipe.created_by = Users.query.filter_by(id=recipe.user_id).first().username # type: ignore
        
# Wtforms

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
        
class AddRecipeForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired(), Length(min=2, max=40)])
    desc = StringField("Description:", validators=[DataRequired(), Length(min=2, max=200)])
    ingredients = TextAreaField("Ingredients:", validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField("Instructions:", validators=[DataRequired(), Length(min=10, max=1000)])
    image = FileField('image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Please only upload an image.')])