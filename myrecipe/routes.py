from enum import Enum
import os
from datetime import datetime
from flask import (url_for, redirect, render_template,
                   request, send_from_directory, flash)
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from flask_bcrypt import Bcrypt
from sqlalchemy import null

# WTForms imports
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Import from init
from myrecipe import db, app
from myrecipe.models import DietaryTags, User, Recipe, SavedRecipe, ModifiedRecipe

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
DIETARY_TAGS = ["vv", "v", "gf", "df", "nf", "ef"]
ADMIN_DEFAULT_PASSWORD = "password"

class UserType(Enum):
    """
    Enumeration for user types.
    
    Attributes:
        STANDARD (str): Standard user type.
        ADMIN (str): Admin user type.
    """
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"


if not app.config["SAVE_IMAGES_LOCALLY"]:
    cloudinary.config(
        cloud_name=os.environ.get("cloud_name"),
        api_key=os.environ.get("api_key"),
        api_secret=os.environ.get("api_secret")
    )


@login_manager.user_loader
def load_user(user_id):
    """Used by login manager to load the user from the database.
    
    Args:
        user_id (int): The ID of the user to load.
    
    Returns:
        User: The user.
    """
    return User.query.get(int(user_id))


@app.context_processor
def inject_date():
    """Template context processor
    
    Injects the current date as 'current_date' into all the templates."""
    return {'current_date': datetime.utcnow()}


# Homepage
@app.route("/")
def home():
    """View the homepage.
    
    Returns:
        Rendered template: The homepage.
    """
    search_form = SearchForm()
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    add_dietary_tags_to_recipes(recipes)
    return render_template("index.html", recipes=recipes, search_form=search_form)


# Login user
@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs in the user
    
    If the user is already logged in, it redirects to the homepage.
    If there is no admin user, it creates an admin user with default password.
    If the login form is  valid, it logs the user in and redirects to the homepage.
    
    Returns:
        Rendered template: The homempage if successful.
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if User.query.filter_by(user_type=UserType.ADMIN.value).first() is None:
        admin = User(username="admin", password=bcrypt.generate_password_hash(ADMIN_DEFAULT_PASSWORD).decode("utf-8"), user_type=UserType.ADMIN.value)
        db.session.add(admin)
        db.session.commit()

    form = LoginForm()

    if request.method == "POST":
        user = get_user(request.form.get("username"))
        if form.validate_on_submit():
            login_user(user)
            if (user.user_type == UserType.ADMIN.value and bcrypt.check_password_hash(user.password, ADMIN_DEFAULT_PASSWORD)):
                flash("Please change the admin password from default.", "danger")
                return redirect(url_for("profile"))
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


# Logout user
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logs user out.
    Returns:
        redirect: The homepage.
    """
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# Register user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user.

    If the user hasn't logged out, it redirects to the homepage.
    
    Returns:
        Rendered template: The login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            encrypted_pass = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(username=username,
                        password=encrypted_pass, user_type=UserType.STANDARD.value)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


# Profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View the current user's profile page.
    
    If the form is valid, update user password and display message.
    
    Returns:
        Rendered template: The profile page.
    """
    form = NewPasswordForm()
    user = User.query.get(current_user.id)

    if request.method == "POST":
        if form.validate_on_submit():
            user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            db.session.add(user)
            db.session.commit()
            flash("Password updated.", "success")
    return render_template("profile.html", user=user, form=form)


# My recipes
@app.route("/my-recipes")
@login_required
def my_recipes():
    """View all recipes created by the current user.

    Returns:
        Rendered template: The my recipes page.
    """
    recipes = [recipe for recipe in get_all_recipes() if user_owns_recipe(current_user.id, recipe)]
    add_created_by_to_recipes(recipes)
    return render_template("my-recipes.html", recipes=recipes)


# View recipe
@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def view_recipe(recipe_id):
    """View recipe page.
    
    Args:
        recipe_id (int): The ID of the recipe to view.
        
    Returns:
        Rendered template: The recipe page.
    """
    recipe_is_saved = has_user_saved_recipe(current_user.id, recipe_id) if current_user.is_authenticated else False
    recipe = Recipe.query.get(recipe_id)
    add_created_by_to_recipes([recipe])
    add_dietary_tags_to_recipes([recipe])

    is_admin = is_user_admin(current_user.id) if current_user.is_authenticated else False

    return render_template("view-recipe.html", recipe=recipe, recipe_is_saved=recipe_is_saved, is_admin=is_admin)


# View modified recipe
@app.route("/modified-recipe/<int:recipe_id>", methods=["GET", "POST"])
def view_modified_recipe(recipe_id):
    """View modified recipe page.
    
    Args:
        recipe_id (int): The ID of the modified recipe to view.
        
    Returns:
        Rendered template: The recipe page.
    """
    recipe = get_modified_recipe(recipe_id)
    add_dietary_tags_to_recipes([recipe])
    add_created_by_to_recipes([recipe])
    
    is_admin = is_user_admin(current_user.id) if current_user.is_authenticated else False
    
    return render_template("view-recipe.html", recipe=recipe, recipe_is_saved=False, is_admin=is_admin)


# Add recipe
@app.route("/add-recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    """Adds a new recipe to the database.
    
    Displays page with a form to add a new recipe.
    If the form is valid, it creates a new recipe and redirects to the page of the new recipe.
    """
    form = AddRecipeForm()
    
    if request.method == "POST":
        title = form.title.data
        desc = form.desc.data
        ingredients = form.ingredients.data.strip()
        instructions = form.instructions.data.strip()
        if form.validate_on_submit():
            image = form.image.data
            if image:
                image_url = save_image(image)
                
            dietary_tags_id = add_dietary_tags_to_db(form.dietary_tags.data)
            recipe = Recipe(user_id=current_user.id, title=title, desc=desc, ingredients=ingredients, instructions=instructions, image_url=image_url if image else null(), dietary_tags_id=dietary_tags_id)
            db.session.add(recipe)
            db.session.commit()

            return redirect(url_for("view_recipe", recipe_id=recipe.id))
    return render_template("add-recipe.html", form=form)


# Add modified recipe
@app.route("/add-modified-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def add_modified_recipe(recipe_id):
    """Adds a modified recipe.
    
    returns:
        redirect: The page of the modified recipe that was added.
    """
    form = AddModifiedRecipeForm()
    original_recipe = Recipe.query.get(recipe_id)
    original_recipe.created_by = User.query.filter_by(id=original_recipe.user_id).first().username
    
    if request.method == "POST":
        if form.validate_on_submit():
            ingredients = form.ingredients.data.strip()
            instructions = form.instructions.data.strip()
            extended_desc = form.extended_desc.data
            dietary_tags_id = add_dietary_tags_to_db(form.dietary_tags.data)
            modified_recipe = ModifiedRecipe(modified_by_id=current_user.id, recipe_id=recipe_id, dietary_tags_id=dietary_tags_id, extended_desc=extended_desc, ingredients=ingredients, instructions=instructions)
            
            db.session.add(modified_recipe)
            db.session.commit()
            return redirect(url_for("view_recipe", recipe_id=modified_recipe.id))
    
    form.ingredients.data = original_recipe.ingredients # type: ignore
    form.instructions.data = original_recipe.instructions # type: ignore
    add_dietary_tags_to_recipes([original_recipe])
    form.dietary_tags.data = dietary_tag_bools_to_data(get_recipe_dietary_tags_bools(original_recipe)) # type: ignore
    
    return render_template("add-modified-recipe.html", form=form, original_recipe=original_recipe)


# Edit recipe
@app.route("/edit-recipe/<int:recipe_id>/<int:modified_recipe>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id, modified_recipe):
    """Updates recipe in the database.
    
    Args:
        recipe_id (int): The ID of the recipe to be edited.
        modified_recipe (int): 0 if the recipe is not modified, 1 if it is.
        
    Returns:
        redirect: The page of the recipe that was edited.
    """
    recipe = get_recipe(recipe_id, modified_recipe)
    add_dietary_tags_to_recipes([recipe])
    if user_owns_recipe(current_user.id, recipe) or is_user_admin(current_user.id):
        form = AddRecipeForm() if not is_modified_recipe(recipe) else AddModifiedRecipeForm()
        if request.method == "POST":
            if form.validate_on_submit():
                ingredients = form.ingredients.data.strip()
                instructions = form.instructions.data.strip()
                
                if is_modified_recipe(recipe):
                    extended_desc = form.extended_desc.data
                    update_modified_recipe(recipe, instructions, ingredients, extended_desc)
                else:
                    title = form.title.data
                    desc = form.desc.data
                    image = form.image.data
                    
                    update_recipe(recipe, title, desc, ingredients, instructions, image)

                update_dietary_tags(recipe, form.dietary_tags.data)
                return redirect(url_for("view_modified_recipe" if is_modified_recipe(recipe) else "view_recipe", recipe_id=recipe.id))
            return render_template("edit-recipe.html", form=form)
        
        set_form_dietary_tags(form, dietary_tag_bools_to_data(get_recipe_dietary_tags_bools(recipe)))
        
        form.ingredients.data = recipe.ingredients # type: ignore
        form.instructions.data = recipe.instructions # type: ignore
        
        if is_modified_recipe(recipe):
            form.extended_desc.data = recipe.extended_desc # type: ignore
            return render_template("edit-modified-recipe.html", form=form, recipe=recipe)
        else:
            form.title.data = recipe.title # type: ignore
            form.desc.data = recipe.desc # type: ignore
            form.image.data = recipe.image_url # type: ignore
            return render_template("edit-recipe.html", form=form, recipe=recipe)    
    flash("You can only edit your own recipes.", "danger")
    return redirect(url_for("my_recipes"))


# Delete recipe
@app.route("/delete-recipe/<int:recipe_id>/<int:modified_recipe>", methods=["GET", "POST"])
@login_required
def delete_recipe(recipe_id, modified_recipe):
    """Delete recipe from the database.

    Args:
        recipe_id (int): The ID of the recipe to be deleted.
        modified_recipe (int): 0 if the recipe is not modified, 1 if it is.

    Returns:
        redirect: Redirects the user to the "my_recipes" page after deleting the recipe.
    """
    recipe = get_recipe(recipe_id, modified_recipe)
    if user_owns_recipe(current_user.id, recipe) or is_user_admin(current_user.id):
        if recipe.image_url and image_exists(recipe.image_url) and not is_modified_recipe(recipe):
            delete_image(recipe.image_url) 
        flash(f'Recipe "{recipe}" deleted.', "success")
        db.session.delete(recipe)
        db.session.commit()
        return redirect(url_for("my_recipes"))

    flash("You can only delete your own recipes.", "danger")
    return redirect(url_for("my_recipes"))


# Saved recipes
@app.route("/view-saved-recipes", methods=["GET"])
@login_required
def view_saved_recipes():
    """App route for displaying saved recipes.

    Retrieves the saved recipes associated with the current user and adds the 'created by' information to each recipe.

    Returns:
        Rendered template: The saved recipes page.
    """
    saved_recipes_keys = SavedRecipe.query.filter_by(user_id=current_user.id).all()

    saved_recipes = [recipe_key.recipe for recipe_key in saved_recipes_keys]
    add_created_by_to_recipes(saved_recipes)

    return render_template("saved-recipes.html", saved_recipes=saved_recipes)


# Save/unsave recipe
@app.route("/toggle-save-recipe/<int:recipe_id>", methods=["POST"])
@login_required
def toggle_save_recipe(recipe_id):
    """Toggle whether user current user has saved recipe.

    Args:
        recipe_id (int): The ID of the recipe to toggle the save for.
    """
    if (has_user_saved_recipe(current_user.id, recipe_id)):
        saved_recipe = SavedRecipe.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        db.session.delete(saved_recipe)
    else:
        saved_recipe = SavedRecipe(user_id=current_user.id, recipe_id=recipe_id) # type: ignore
        db.session.add(saved_recipe)

    db.session.commit()


# Search recipes
@app.route("/search", methods=["GET"])
def search():
    """Handles the GET request when searching and returns the results.

    It validates the search form then performs a search based on the query and dietary filters.

    Returns:
        The search results page or the home page with an error message.

    """
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
    """Retrieve image file from the UPLOAD_FOLDER.

    Args:
        filename (str): The name of the image file to retrieve.

    Returns:
        (image): The image file as an attachment.

    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


# Error handling
@app.errorhandler(401)
def unauthorized(e):
    """Handles 401 error."""
    return render_template("error-pages/401.html", e=e), 401


@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 error."""
    return render_template("error-pages/404.html", e=e), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Handles 405 error."""
    return render_template("error-pages/405.html", e=e), 405


@app.errorhandler(500)
def internal_server_error(e):
    """Handles 500 error."""
    return render_template("error-pages/500.html", e=e), 500


# Helpers
def get_user(username):
    """Retrieve user from database based using their username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        User: The user object or None if the user does not exist.
    """
    return User.query.filter_by(username=username).first()


def get_all_recipes():
    """Retrieves all original and modified recipes from the database.

    Returns:
        list: A list of all recipes.
    """
    all_recipes = Recipe.query.all()
    all_recipes.extend(get_all_modified_recipes())
    return all_recipes


def get_all_modified_recipes():
    """Retrieves all modified recipes from the database.

    Returns:
        modified recipes (list): A list of modified recipes.
    """
    modified_recipes = ModifiedRecipe.query.all()
  
    for m_recipe in modified_recipes:
        m_recipe = get_modified_recipe(m_recipe.id)

    return modified_recipes


def get_recipe(recipe_id, get_modified=False):
    """Get a recipe by ID.

    Args:
        recipe_id (int): The ID of the recipe to retrieve.
        get_modified (bool): If True, get a modified recipe.

    Returns:
        recipe: The retrieved recipe.
    """
    if get_modified:
        recipe = get_modified_recipe(recipe_id)
    else:
        recipe = Recipe.query.get(recipe_id)
    return recipe


def add_recipe_data_to_modified_recipes(modified_recipe):
    """Adds the data from the original recipe to the modified recipe.

    Args:
        modified_recipe (list): A list of modified recipe objects.
    """
    for m_recipe in modified_recipe:
        recipe = Recipe.query.get(m_recipe.recipe_id)
        m_recipe.title = recipe.title
        m_recipe.desc = recipe.desc
        m_recipe.image_url = recipe.image_url
        m_recipe.modified_by = User.query.filter_by(id=m_recipe.modified_by_id).first().username
   

def get_modified_recipe(recipe_id):
    """Get modified recipe from the database using the recipe ID.
    
    Args:
        recipe_id (int): The ID of the recipe to retrieve.
    
    Returns:
        ModifiedRecipe: The modified recipe.
    """
    recipe = ModifiedRecipe.query.get(recipe_id)
    add_recipe_data_to_modified_recipes([recipe])
    return recipe


def add_dietary_tags_to_db(form_dietary_tags):
    """Add dietary tags to the database.

    Args:
        form_dietary_tags (str list): A list of dietary tags strings.

    Returns:
        int: The ID of the added dietary tags.
    """
    dietary_tags = DietaryTags(is_vegan="vv" in form_dietary_tags, is_vegetarian="v" in form_dietary_tags, is_gluten_free="gf" in form_dietary_tags, is_dairy_free="df" in form_dietary_tags, is_nut_free="nf" in form_dietary_tags, is_egg_free="ef" in form_dietary_tags) # type: ignore
    db.session.add(dietary_tags)
    db.session.commit()
    return dietary_tags.id

       
def add_created_by_to_recipes(recipes):
    """Adds the created_by attribute to the recipes

    Args:
        recipes (list): The recipes to add the created_by attribute to.
    """
    for recipe in recipes:
        user_id = recipe.original_recipe.user_id if is_modified_recipe(recipe) else recipe.user_id
        recipe.created_by = User.query.filter_by(id=user_id).first().username


def has_user_saved_recipe(user_id, recipe_id):
    """Check if user has saved the recipe
    
    args:
        user_id (int): The user id.
        recipe_id (int): The recipe id.
        
    returns: 
        bool: True if user has saved the recipe else false.
    """
    return bool(SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()) 


def save_image(image):
    """Decides whether image is uploaded or stored locally

    Args:
        image: The image to be saved or uploaded.

    Returns:
        str: The url of the image.
    """
    if app.config["SAVE_IMAGES_LOCALLY"]:
        return save_image_locally(image)
    else:
        return upload_image(image)


def upload_image(image):
    """Uploads an image to cloudinary and returns the URL of the uploaded image.

    Parameters:
    image (str): The image to be saved.

    Returns: 
        str: The URL of the uploaded image.
    """
    result = cloudinary.uploader.upload(image, public_id=image.filename, folder="myrecipe/image-uploads")
    image_url = result['secure_url']
    return image_url


def save_image_locally(image):  
    """Saves an image locally
    
    Args:
        file: The image to be saved.
        
    returns: The image URL
    """
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
    """Deletes an image from the local storage or cloud storage.

    Args:
        image_url (str): The URL of the image to be deleted.
    """
    if app.config["SAVE_IMAGES_LOCALLY"]:
        os.remove(app.config["PACKAGE_NAME"] + "/" + image_url)
    else:
        cloudinary.uploader.destroy(image_url)


def image_exists(image_url):
    """Check if the image exists in the specified path.

    Args:
        image_url (str): The URL of the image file.

    Returns:
       bool: True if the image file exists, False otherwise.
    """
    if app.config["SAVE_IMAGES_LOCALLY"]:
        return os.path.exists(app.config["PACKAGE_NAME"] + "/" + image_url)
    else:
        False


def user_owns_recipe(user_id, recipe):
    """Check if the user owns the recipe.

    Args:
        user_id (int): The ID of the user.
        recipe (Recipe): The recipe to check.

    Returns:
        bool: True if the user owns the recipe, False otherwise.
    """
    if is_modified_recipe(recipe):
        # If modified recipe, check the modified_by_id with user_id
        return recipe.modified_by_id == user_id # type: ignore
    else:
        # If normal recipe, just check the user_id with user_id
        return recipe.user_id == user_id


def search_all_recipes(search_query, *args):
    """Search for recipes that match the given search query and apply dietary tags filter.

    Args:
        search_query (str): The search query to match against recipe titles and descriptions.
        *args: Variable number of arguments representing dietary tags filter.

    Returns:
        list: Recipes that match the search query and dietary tags filter.
    """
    # Get all recipes that match the search query
    recipes = Recipe.query.filter(Recipe.title.ilike(f"%{search_query}%")).all()
    recipes.extend(Recipe.query.filter(Recipe.desc.ilike(f"%{search_query}%")).all())

    # Get all modified recipes that match the search query
    modified_recipes = ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(Recipe.title.ilike(f"%{search_query}%")).all() #type: ignore
    modified_recipes.extend(ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(Recipe.desc.ilike(f"%{search_query}%")).all()) #type: ignore
    add_recipe_data_to_modified_recipes(modified_recipes)

    # Extend recipes with modified recipes
    recipes.extend(modified_recipes)
    recipes = set(recipes) # Remove duplicates

    # Create dietary tags boolean filter
    add_dietary_tags_to_recipes(recipes)
    dietary_tags_filter = dietary_tag_data_to_bools(args[0])

    # Apply dietary tags filter
    if True in dietary_tags_filter:
        filtered_recipes = []
        for recipe in recipes:
            recipe_filter = get_recipe_dietary_tags_bools(recipe)
            passed = [recipe_filter[i] for i in range(len(dietary_tags_filter)) if dietary_tags_filter[i]]
   
            if all(passed):
                filtered_recipes.append(recipe)
    else:
        filtered_recipes = recipes
        
    return filtered_recipes

def set_form_dietary_tags(form, dietary_tag_values):
    """ 
    Sets the forms dietary tags to the values provided.
    [https://stackoverflow.com/questions/5519729/wtforms-how-to-select-options-in-selectmultiplefield]
        
    Args:
        form (FlaskForm): The form to set the dietary tags for.
        dietary_tag_values (str list): The dietary tags to set the form to.  
    """
    form.dietary_tags.default = dietary_tag_values
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
    if len(dietary_tags) == 0:
        return []
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


def is_modified_recipe(recipe):
    return hasattr(recipe, "original_recipe")


def update_recipe(recipe, title, desc, ingredients, instructions, image):
    if title != recipe.title:
        recipe.title = title
    if desc != recipe.desc:
        recipe.desc = desc
    if ingredients != recipe.ingredients:
        recipe.ingredients = ingredients
    if instructions != recipe.instructions:
        recipe.instructions = instructions
    if image:
        if image.filename != recipe.image_url.split("/")[-1] or not image_exists(recipe.image_url):
                if image_exists(recipe.image_url):
                    delete_image(recipe.image_url)
                recipe.image_url = save_image(image)
    db.session.add(recipe)
    db.session.commit()


def update_modified_recipe(recipe, instructions, ingredients, extended_desc):
    if extended_desc != recipe.extended_desc:
        recipe.extended_desc = extended_desc
    if ingredients != recipe.ingredients:
        recipe.ingredients = ingredients
    if instructions != recipe.instructions:
        recipe.instructions = instructions
    db.session.add(recipe)
    db.session.commit()


def update_dietary_tags(recipe, new_dietary_tags_data):
    dietary_tags = DietaryTags.query.get(recipe.dietary_tags_id)
    dietart_tag_data = dietary_tag_bools_to_data(get_recipe_dietary_tags_bools(recipe))
    if dietart_tag_data != new_dietary_tags_data:
        dietary_tags.is_vegan = "vv" in new_dietary_tags_data
        dietary_tags.is_vegetarian = "v" in new_dietary_tags_data
        dietary_tags.is_gluten_free = "gf" in new_dietary_tags_data
        dietary_tags.is_dairy_free = "df" in new_dietary_tags_data
        dietary_tags.is_nut_free = "nf" in new_dietary_tags_data
        dietary_tags.is_egg_free = "ef" in new_dietary_tags_data
        db.session.add(dietary_tags)
        db.session.commit()

 
def is_user_admin(user_id):
    return User.query.filter_by(id=user_id, user_type=UserType.ADMIN.value).first() != None

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
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])
    
class AddModifiedRecipeForm(FlaskForm):
    extended_desc = StringField("Extended description:",
                                validators=[DataRequired(), Length(min=2, max=100)])
    ingredients = TextAreaField("Ingredients:",
                                validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField("Instructions:",
                                 validators=[DataRequired(), Length(min=10, max=1000)])

    # Dietary tags
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])

class SearchForm(FlaskForm):
    search_bar = StringField("Search:")
     # Dietary tags
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Veggie"), ("gf", "GF"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])

    def validate_search_bar(self, search_bar):
        if not search_bar.data and not self.dietary_tags.data:
            raise ValidationError("Please enter a search query or select a filter.")
        
class NewPasswordForm(FlaskForm):
    current_password = PasswordField("Current password:", validators=[DataRequired(), Length(min=8, max=20)])
    new_password = PasswordField("New password:", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField("Confirm new password:", validators=[DataRequired(), EqualTo("new_password", "Passwords must match.")])

    def validate_current_password(self, current_password):
        if not bcrypt.check_password_hash(User.query.get(current_user.id).password, self.current_password.data):
            raise ValidationError("Current password is incorrect.")
    
    def validate_confirm_password(self, new_password):
        if bcrypt.check_password_hash(User.query.get(current_user.id).password, self.new_password.data):
            raise ValidationError("New password cannot be the same as the current password.")