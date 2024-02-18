import os
from flask import url_for, redirect, render_template, request, send_from_directory, flash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, login_user
from flask_bcrypt import Bcrypt
from sqlalchemy import null
from myrecipe import db, app
from myrecipe.models import DietaryTags, User, Recipe, SavedRecipe, ModifiedRecipe

# WTForms imports
from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Homepage
@app.route("/")
def home():
    search_form = SearchForm()
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    return render_template("index.html", recipes=recipes, search_form=search_form)

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
            flash(f"Welcome back, {user.username}!", "success") # type: ignore
            return redirect(url_for("home"))
    return render_template("login.html", form=form)

# Logout user
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
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
            user = User(username=username, password=encrypted_pass) # type: ignore
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        
    return render_template("register.html", form=form)

# My recipies
@app.route("/my-recipes")
@login_required
def my_recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    
    add_created_by_to_recipes(recipes)
    return render_template("my-recipes.html", recipes=recipes)

# View recipe
@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def view_recipe(recipe_id):
    recipe_is_saved = has_user_saved_recipe(current_user.id, recipe_id) if current_user.is_authenticated else False  
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        recipe = get_modified_recipe(recipe_id)
    add_created_by_to_recipes([recipe])
    
    return render_template("view-recipe.html", recipe=recipe, recipe_is_saved=recipe_is_saved)

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
            if image:
                image_url = save_image_locally(image)
                
            recipe = Recipe(user_id=current_user.id, title=title, desc=desc, ingredients=ingredients, instructions=instructions, image_url=image_url if image else null()) # type: ignore
            db.session.add(recipe)
            db.session.commit()   
                     
            dietary_tags = DietaryTags(recipe_id=recipe.id, is_vegan="vv" in form.dietary_tags.data, is_vegetarian="v" in form.dietary_tags.data, is_gluten_free="gf" in form.dietary_tags.data, is_dairy_free="df" in form.dietary_tags.data, is_nut_free="nf" in form.dietary_tags.data, is_egg_free="ef" in form.dietary_tags.data) # type: ignore
            db.session.add(dietary_tags)
            db.session.commit()
            return redirect(url_for("view_recipe", recipe_id=recipe.id))
    return render_template("add-recipe.html", form=form)

# Add modified recipe
@app.route("/add-modified-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def add_modified_recipe(recipe_id):
    form = AddModifiedRecipeForm()
    original_recipe = Recipe.query.get(recipe_id)
    original_recipe.created_by = User.query.filter_by(id=original_recipe.user_id).first().username # type: ignore
    
    if request.method == "POST":
        if form.validate_on_submit():
            ingredients = form.ingredients.data
            instructions = form.instructions.data
            extended_desc = form.extended_desc.data
            modified_recipe = ModifiedRecipe(modified_by_id=current_user.id, recipe_id=recipe_id, extended_desc=extended_desc, ingredients=ingredients, instructions=instructions) # type: ignore
            
            db.session.add(modified_recipe)
            db.session.commit()
            return redirect(url_for("view_recipe", recipe_id=modified_recipe.id))
    
    form.ingredients.data = original_recipe.ingredients # type: ignore
    form.instructions.data = original_recipe.instructions # type: ignore
    
    return render_template("add-modified-recipe.html", form=form, original_recipe=original_recipe)
    

# Delete recipe
@app.route("/delete-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def delete_recipe(recipe_id):
    recipe = get_recipe(recipe_id)
    if user_owns_recipe(current_user.id, recipe): #type: ignore
        db.session.delete(recipe)
        db.session.commit()
        flash(f'Recipe "{recipe}" deleted.', "success")
        return redirect(url_for("my_recipes"))

    flash("You can only delete your own recipes.", "danger")
    return redirect(url_for("my_recipes"))

# Saved recipes
@app.route("/view-saved-recipes", methods=["GET"])
@login_required
def view_saved_recipes():
    saved_recipes_keys = SavedRecipe.query.filter_by(user_id=current_user.id).all()
    
    saved_recipes = [recipe_key.recipe for recipe_key in saved_recipes_keys]
    add_created_by_to_recipes(saved_recipes)
        
    return render_template("saved-recipes.html", saved_recipes=saved_recipes)

# Save/unsave recipe
@app.route("/toggle-save-recipe/<int:recipe_id>", methods=["POST"])
@login_required
def toggle_save_recipe(recipe_id):
    if(has_user_saved_recipe(current_user.id, recipe_id)):
        saved_recipe = SavedRecipe.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        db.session.delete(saved_recipe)
    else:
        saved_recipe = SavedRecipe(user_id=current_user.id, recipe_id=recipe_id) # type: ignore
        db.session.add(saved_recipe)
    
    db.session.commit()
    return redirect(url_for("view_recipe", recipe_id=recipe_id))

# Search recipes
@app.route("/search", methods=["GET"])
def search():
    # Need to state no crsf token for search form [https://stackoverflow.com/questions/61237524/validating-get-params-with-wtforms-in-flask]
    search_form = SearchForm(request.args, meta={'csrf': False})

    if search_form.validate():
        search_query_url = request.query_string.decode("utf-8").split("&")[0].split("=")
        search_query = search_query_url[1] 
        recipes = search_all_recipes(search_query)
        add_created_by_to_recipes(recipes)
        return render_template("search-results.html", recipes=recipes, search_query=search_query)
    # If doesn't validate, redirect to home with error message.
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    return render_template("index.html", recipes=recipes, search_form=search_form, scroll="search-box")

# Get image - From Flask documentation
@app.route("/image-uploads/<path:filename>")
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    
# Error handling
@app.errorhandler(401)
def unauthorized(e):
    return render_template("error-pages/401.html", e=e), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error-pages/404.html", e=e), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("error-pages/405.html", e=e), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error-pages/500.html", e=e), 500

# Helpers
def get_user(username):
    return User.query.filter_by(username=username).first()

def get_all_recipes():
    all_recipes = Recipe.query.all()
    modified_recipes = ModifiedRecipe.query.all()
    
    for m_recipe in modified_recipes:
        m_recipe = get_modified_recipe(m_recipe.id)
        
    all_recipes.extend(modified_recipes)
    return all_recipes

def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        recipe = get_modified_recipe(recipe_id)
    return recipe

def get_modified_recipe(recipe_id):
    recipe = ModifiedRecipe.query.get(recipe_id)
    recipe.title = recipe.original_recipe.title # type: ignore
    recipe.desc = recipe.original_recipe.desc # type: ignore
    recipe.image_url = recipe.original_recipe.image_url # type: ignore
    recipe.modified_by = User.query.filter_by(id=recipe.modified_by_id).first().username # type: ignore
    return recipe

def add_created_by_to_recipes(recipes):
    for recipe in recipes:
        user_id = recipe.original_recipe.user_id if hasattr(recipe, "original_recipe") else recipe.user_id # type: ignore
        recipe.created_by = User.query.filter_by(id=user_id).first().username # type: ignore            
        
def has_user_saved_recipe(user_id, recipe_id):
    return bool(SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()) 

def save_image_locally(image):
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config["PACKAGE_NAME"] + "/" + app.config['UPLOAD_FOLDER'], filename))
                
    return "/" + app.config["UPLOAD_FOLDER"] + "/" + filename 

def user_owns_recipe(user_id, recipe):
    if hasattr(recipe, "modified_by_id"):
        # If modified recipe, check the modified_by_id with user_id
        return recipe.modified_by_id == user_id # type: ignore
    else:
        # If normal recipe, just check the user_id with user_id
        return recipe.user_id == user_id
    
def search_all_recipes(search_query):
    recipes = Recipe.query.filter(Recipe.title.ilike(f"%{search_query}%")).all()
    recipes.extend(Recipe.query.filter(Recipe.desc.ilike(f"%{search_query}%")).all())
    return recipes

def set_default_dietary_tags(form, default_values):
    # Set default dietary tags [https://stackoverflow.com/questions/5519729/wtforms-how-to-select-options-in-selectmultiplefield]
    form.dietary_tags.default = default_values
    form.process()  
        
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
    image = FileField('image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Please only upload an image (jpg, png, or webp).')])
    
    # Dietary tags
    dietary_tags = SelectMultipleField("Dietary tags:", choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("e", "Egg-free")], validators=[DataRequired()])
    
class AddModifiedRecipeForm(FlaskForm):
    extended_desc = StringField("Extended description:", validators=[DataRequired(), Length(min=2, max=100)])
    ingredients = TextAreaField("Ingredients:", validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField("Instructions:", validators=[DataRequired(), Length(min=10, max=1000)])
    
class SearchForm(FlaskForm):
    search_bar = StringField("Search:", validators=[DataRequired(), Length(min=2, max=40)])