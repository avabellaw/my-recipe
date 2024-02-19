import os
from flask import url_for, redirect, render_template, request, send_from_directory, flash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, login_user
from flask_bcrypt import Bcrypt
from sqlalchemy import Boolean, null
from myrecipe import db, app
from myrecipe.models import DietaryTags, User, Recipe, SavedRecipe, ModifiedRecipe

# WTForms imports
from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, PasswordField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
DIETARY_TAGS = ["vv", "v", "gf", "df", "nf", "ef"]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Homepage
@app.route("/")
def home():
    search_form = SearchForm()
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    add_dietary_tags_to_recipes(recipes)
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
    recipes = [recipe for recipe in get_all_recipes() if user_owns_recipe(current_user.id, recipe)]
    recipes.extend(get_all_modified_recipes())
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
    add_dietary_tags_to_recipes([recipe])
    
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
                
            dietary_tags_id = add_dietary_tags_to_db(form.dietary_tags.data)
            recipe = Recipe(user_id=current_user.id, title=title, desc=desc, ingredients=ingredients, instructions=instructions, image_url=image_url if image else null(), dietary_tags_id=dietary_tags_id) # type: ignore
            db.session.add(recipe)
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
            dietary_tags_id = add_dietary_tags_to_db(form.dietary_tags.data)
            modified_recipe = ModifiedRecipe(modified_by_id=current_user.id, recipe_id=recipe_id, dietary_tags_id=dietary_tags_id, extended_desc=extended_desc, ingredients=ingredients, instructions=instructions) # type: ignore
            
            db.session.add(modified_recipe)
            db.session.commit()
            return redirect(url_for("view_recipe", recipe_id=modified_recipe.id))
    
    form.ingredients.data = original_recipe.ingredients # type: ignore
    form.instructions.data = original_recipe.instructions # type: ignore
    add_dietary_tags_to_recipes([original_recipe])
    form.dietary_tags.data = dietary_tag_bools_to_data(get_recipe_dietary_tags_bools(original_recipe)) # type: ignore
    
    return render_template("add-modified-recipe.html", form=form, original_recipe=original_recipe)

# Edit recipe
@app.route("/edit-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    recipe = get_recipe(recipe_id)
    add_dietary_tags_to_recipes([recipe])
    if user_owns_recipe(current_user.id, recipe): #type: ignore
        form = AddRecipeForm()
        if request.method == "POST":
            if form.validate_on_submit():
                title = form.title.data
                desc = form.desc.data 
                ingredients = form.ingredients.data
                instructions = form.instructions.data
                
                if title != recipe.title:
                    recipe.title = title
                if desc != recipe.desc:
                    recipe.desc = desc
                if ingredients != recipe.ingredients:
                    recipe.ingredients = ingredients
                if instructions != recipe.instructions:
                    recipe.instructions = instructions
                image = form.image.data
                if image.filename != recipe.image_url.split("/")[-1]:
                    if image:
                        delete_image(recipe.image_url)
                        recipe.image_url = save_image_locally(image)
                db.session.add(recipe)
                db.session.commit()
                return redirect(url_for("view_recipe", recipe_id=recipe.id))
            return render_template("edit-recipe.html", form=form)
        set_default_dietary_tags(form, dietary_tag_bools_to_data(get_recipe_dietary_tags_bools(recipe)))
        form.title.data = recipe.title # type: ignore
        form.desc.data = recipe.desc # type: ignore
        form.ingredients.data = recipe.ingredients # type: ignore
        form.instructions.data = recipe.instructions # type: ignore
        form.image.data = recipe.image_url # type: ignore
        return render_template("edit-recipe.html", form=form, recipe=recipe)    
    flash("You can only edit your own recipes.", "danger")
    return redirect(url_for("my_recipes"))

# Delete recipe
@app.route("/delete-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def delete_recipe(recipe_id):
    recipe = get_recipe(recipe_id)
    if user_owns_recipe(current_user.id, recipe):
        if recipe.image_url and os.path.exists(app.config["PACKAGE_NAME"] + "/" + recipe.image_url):
            delete_image(recipe.image_url) 
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
        url_parts = request.query_string.decode("utf-8").split("&")
        
        dietary_tags = []
        for url_part in url_parts:
            if url_part.startswith("search_bar"):
                search_query_url = url_parts[0].split("=")
                search_query = search_query_url[1] 
            if url_part.startswith("dietary_tags"):
                dietary_tags.append(url_part.split("=")[1])
                
        recipes = search_all_recipes(search_query, dietary_tags)
        add_created_by_to_recipes(recipes)
        search_form = SearchForm()
        dietary_tags = dietary_tag_data_to_names(dietary_tags)
        return render_template("search-results.html", recipes=recipes, search_query=search_query, dietary_tags=dietary_tags, search_form=search_form)
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
    all_recipes.extend(get_all_modified_recipes())
    return all_recipes

def get_all_modified_recipes():
    modified_recipes = ModifiedRecipe.query.all()
        
    for m_recipe in modified_recipes:
        m_recipe = get_modified_recipe(m_recipe.id)
    
    return modified_recipes

def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        recipe = get_modified_recipe(recipe_id)
    return recipe

def add_recipe_data_to_modified_recipes(modified_recipe):
    for m_recipe in modified_recipe:
        recipe = Recipe.query.get(m_recipe.recipe_id)
        m_recipe.title = recipe.title # type: ignore
        m_recipe.desc = recipe.desc # type: ignore
        m_recipe.image_url = recipe.image_url # type: ignore
        m_recipe.modified_by = User.query.filter_by(id=m_recipe.modified_by_id).first().username # type: ignore
   

def get_modified_recipe(recipe_id):
    recipe = ModifiedRecipe.query.get(recipe_id)
    add_recipe_data_to_modified_recipes([recipe])
    return recipe

def add_dietary_tags_to_db(form_dietary_tags):
    dietary_tags = DietaryTags(is_vegan="vv" in form_dietary_tags, is_vegetarian="v" in form_dietary_tags, is_gluten_free="gf" in form_dietary_tags, is_dairy_free="df" in form_dietary_tags, is_nut_free="nf" in form_dietary_tags, is_egg_free="ef" in form_dietary_tags) # type: ignore
    db.session.add(dietary_tags)
    db.session.commit()
    return dietary_tags.id
            
def add_created_by_to_recipes(recipes):
    for recipe in recipes:
        user_id = recipe.original_recipe.user_id if hasattr(recipe, "original_recipe") else recipe.user_id # type: ignore
        recipe.created_by = User.query.filter_by(id=user_id).first().username # type: ignore            
        
def has_user_saved_recipe(user_id, recipe_id):
    return bool(SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()) 

def save_image_locally(image):  
    filename = secure_filename(image.filename)
    save_path = app.config["PACKAGE_NAME"] + "/" + app.config['UPLOAD_FOLDER']
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    counter = 2
    # If file with same name exists, add a number to the end of the filename and increment until a unique filename is found
    while os.path.isfile(os.path.join(save_path, filename)):
        filename_parts = filename.split(".")
        filename_name = filename_parts[0]
        if "_" in filename_name:
            filename_name = filename_name.split("_")[0] + f"_{counter}"
        else:
            filename_name = filename_name + "_2"
        filename = f'{filename_name}.{".".join(filename_parts[1:])}'
        counter+=1

    image.save(os.path.join(save_path, filename))
                
    return "/" + app.config["UPLOAD_FOLDER"] + "/" + filename 

def delete_image(image_url):
    os.remove(os.path.join(app.config["PACKAGE_NAME"] + "/" + image_url))

def user_owns_recipe(user_id, recipe):
    if hasattr(recipe, "modified_by_id"):
        # If modified recipe, check the modified_by_id with user_id
        return recipe.modified_by_id == user_id # type: ignore
    else:
        # If normal recipe, just check the user_id with user_id
        return recipe.user_id == user_id
    
def search_all_recipes(search_query, *args):
    # Get all recipes that match the search query
    recipes = Recipe.query.filter(Recipe.title.ilike(f"%{search_query}%")).all()
    recipes.extend(Recipe.query.filter(Recipe.desc.ilike(f"%{search_query}%")).all())
    
    # Get all modified recipes that match the search query
    modified_recipes = ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(Recipe.title.ilike(f"%{search_query}%")).all() #type: ignore
    modified_recipes.extend(ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(Recipe.desc.ilike(f"%{search_query}%")).all()) #type: ignore
    add_recipe_data_to_modified_recipes(modified_recipes)
    
    # Extend recipes with modified recipes
    recipes.extend(modified_recipes) # type: ignore
    recipes = set(recipes) # Remove duplicates
    add_dietary_tags_to_recipes(recipes)
    filter = dietary_tag_data_to_bools(args[0])
    
    # Apply dietary tags filter
    if True in filter:
        filtered_recipes = []
        for recipe in recipes:
            recipe_filter = get_recipe_dietary_tags_bools(recipe)
            passed = [recipe_filter[i] for i in range(len(filter)) if filter[i]]
            
            if all(passed):
                filtered_recipes.append(recipe)
    else:
        filtered_recipes = recipes
                
    return filtered_recipes

def set_default_dietary_tags(form, default_values):
    # Set default dietary tags [https://stackoverflow.com/questions/5519729/wtforms-how-to-select-options-in-selectmultiplefield]
    form.dietary_tags.default = default_values
    form.process()  

def add_dietary_tags_to_recipes(recipes):
    for recipe in recipes:
        tags = DietaryTags.query.filter_by(id=recipe.dietary_tags_id).first()
        if tags:
            recipe.is_vegan = tags.is_vegan # type: ignore
            recipe.is_vegetarian = tags.is_vegetarian # type: ignore
            recipe.is_gluten_free = tags.is_gluten_free # type: ignore
            recipe.is_dairy_free = tags.is_dairy_free # type: ignore
            recipe.is_nut_free = tags.is_nut_free # type: ignore
            recipe.is_egg_free = tags.is_egg_free # type: ignore
        
            recipe.has_dietary_tags = any([recipe.is_vegan, recipe.is_vegetarian, recipe.is_gluten_free, recipe.is_dairy_free, recipe.is_nut_free, recipe.is_egg_free]) # type: ignore
        else:
            recipe.has_dietary_tags = False
            
def dietary_tag_data_to_bools(dietary_tags):
    return [tag in dietary_tags for tag in DIETARY_TAGS]

def dietary_tag_data_to_names(dietary_tags):
    dietary_str = ",".join(dietary_tags)
    dietary_str = dietary_str.replace("vv", "Vegan")
    dietary_str = dietary_str.replace("v", "Vegetarian")
    dietary_str = dietary_str.replace("gf", "Gluten-free")
    dietary_str = dietary_str.replace("df", "Dairy-free")
    dietary_str = dietary_str.replace("nf", "Nut-free")
    dietary_str = dietary_str.replace("ef", "Egg-free")
    return dietary_str.split(",")

def dietary_tag_bools_to_data(dietary_tags):
    return [tag for tag in DIETARY_TAGS if dietary_tags[DIETARY_TAGS.index(tag)]]

def get_recipe_dietary_tags_bools(recipe):
    return [recipe.is_vegan, recipe.is_vegetarian, recipe.is_gluten_free, recipe.is_dairy_free, recipe.is_nut_free, recipe.is_egg_free]

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
    dietary_tags = SelectMultipleField("Dietary tags:", choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])
    
class AddModifiedRecipeForm(FlaskForm):
    extended_desc = StringField("Extended description:", validators=[DataRequired(), Length(min=2, max=100)])
    ingredients = TextAreaField("Ingredients:", validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField("Instructions:", validators=[DataRequired(), Length(min=10, max=1000)])
    
    # Dietary tags
    dietary_tags = SelectMultipleField("Dietary tags:", choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])
    
class SearchForm(FlaskForm):
    search_bar = StringField("Search:")
     # Dietary tags
    dietary_tags = SelectMultipleField("Dietary tags:", choices=[("vv", "Vegan"), ("v", "Veggie"), ("gf", "GF"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])
    
    def validate_search_bar(self, search_bar):
        if not search_bar.data and not self.dietary_tags.data:
            raise ValidationError("Please enter a search query or select a filter.")
    