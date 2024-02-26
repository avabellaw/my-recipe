"""
Contains the routes for the My Recipe application.

Functions:

    load_user(user_id): Used by login manager to load user from the database.
    inject_date(): Template context processor to inject the current date into all templates.
    home(): Route for homepage.
    login(): Route for login page.
    logout(): Route for logging out.
    register(): Route for registration page.
    profile(): Route for profile page to change password.
    my_recipes(): Route for my recipes page.
    view_recipe(recipe_id): Route for page to view a recipe.
    view_modified_recipe(recipe_id): Route for page to view a modified recipe.
    add_recipe(): Route for page to add a recipe.
    add_modified_recipe(recipe_id): Route for page to add a modified recipe.
"""

import os
from datetime import datetime
from flask import (url_for, redirect, render_template,
                   request, send_from_directory, flash)
from flask_login import (login_user, logout_user,
                         current_user, login_required)
from sqlalchemy import null

import cloudinary
import cloudinary.uploader
import cloudinary.api

from myrecipe import db, app, UserType, bcrypt, DEFAULT_ADMIN_PASSWORD, login_manager
from myrecipe.models import User, Recipe, ModifiedRecipe, SavedRecipe
from myrecipe.helpers import (get_all_recipes, add_created_by_to_recipes,
                              add_dietary_tags_to_recipes, get_user,
                              user_owns_recipe, is_user_admin, save_image,
                              has_user_saved_recipe, get_modified_recipe,
                              is_modified_recipe, update_modified_recipe,
                              update_recipe, update_dietary_tags,
                              delete_image, search_all_recipes,
                              dietary_tag_bools_to_data, get_recipe_dietary_tags_bools,
                              set_form_dietary_tags, dietary_tag_data_to_names,
                              add_dietary_tags_to_db, get_recipe, image_exists)
# Import wtforms
from myrecipe.forms import (RegistrationForm, LoginForm,
                            AddRecipeForm, AddModifiedRecipeForm,
                            SearchForm, NewPasswordForm)

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
        admin = User(username="admin", password=bcrypt.generate_password_hash(
            DEFAULT_ADMIN_PASSWORD).decode("utf-8"), user_type=UserType.ADMIN.value)
        db.session.add(admin)
        db.session.commit()

    form = LoginForm()

    if request.method == "POST":
        user = get_user(request.form.get("username"))
        if form.validate_on_submit():
            login_user(user)
            if (user.user_type == UserType.ADMIN.value
                    and bcrypt.check_password_hash(user.password, DEFAULT_ADMIN_PASSWORD)):
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
            encrypted_pass = bcrypt.generate_password_hash(
                password).decode("utf-8")
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
            user.password = bcrypt.generate_password_hash(
                form.new_password.data).decode("utf-8")
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
    recipes = [recipe for recipe in get_all_recipes(
    ) if user_owns_recipe(current_user.id, recipe)]
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
    recipe_is_saved = has_user_saved_recipe(
        current_user.id, recipe_id) if current_user.is_authenticated else False
    recipe = Recipe.query.get(recipe_id)
    add_created_by_to_recipes([recipe])
    add_dietary_tags_to_recipes([recipe])

    is_admin = is_user_admin(
        current_user.id) if current_user.is_authenticated else False

    return render_template("view-recipe.html",
                           recipe=recipe,
                           recipe_is_saved=recipe_is_saved,
                           is_admin=is_admin)


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

    is_admin = is_user_admin(
        current_user.id) if current_user.is_authenticated else False

    return render_template("view-recipe.html",
                           recipe=recipe,
                           recipe_is_saved=False,
                           is_admin=is_admin)


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
            recipe = Recipe(user_id=current_user.id, title=title, desc=desc,
                            ingredients=ingredients, instructions=instructions,
                            image_url=image_url if image else null(),
                            dietary_tags_id=dietary_tags_id)
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
    original_recipe.created_by = User.query.filter_by(
        id=original_recipe.user_id).first().username

    if request.method == "POST":
        if form.validate_on_submit():
            ingredients = form.ingredients.data.strip()
            instructions = form.instructions.data.strip()
            extended_desc = form.extended_desc.data
            dietary_tags_id = add_dietary_tags_to_db(form.dietary_tags.data)
            modified_recipe = ModifiedRecipe(modified_by_id=current_user.id,
                                             recipe_id=recipe_id,
                                             dietary_tags_id=dietary_tags_id,
                                             extended_desc=extended_desc,
                                             ingredients=ingredients,
                                             instructions=instructions)

            db.session.add(modified_recipe)
            db.session.commit()
            return redirect(url_for("view_modified_recipe", recipe_id=modified_recipe.id))

    form.ingredients.data = original_recipe.ingredients
    form.instructions.data = original_recipe.instructions
    add_dietary_tags_to_recipes([original_recipe])
    form.dietary_tags.data = dietary_tag_bools_to_data(
        get_recipe_dietary_tags_bools(original_recipe))

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
        form = AddRecipeForm() if not is_modified_recipe(
            recipe) else AddModifiedRecipeForm()
        if request.method == "POST":
            if form.validate_on_submit() and False:
                ingredients = form.ingredients.data.strip()
                instructions = form.instructions.data.strip()

                if is_modified_recipe(recipe):
                    extended_desc = form.extended_desc.data
                    update_modified_recipe(
                        recipe, instructions, ingredients, extended_desc)
                else:
                    title = form.title.data
                    desc = form.desc.data
                    image = form.image.data

                    update_recipe(recipe, title, desc,
                                  ingredients, instructions, image)

                update_dietary_tags(recipe, form.dietary_tags.data)
                return redirect(url_for("view_modified_recipe" if is_modified_recipe(recipe)
                                        else "view_recipe", recipe_id=recipe.id))
            if not is_modified_recipe(recipe):
                form.image.data = recipe.image_url
            return render_template("edit-modified-recipe.html" if is_modified_recipe(recipe)
                                   else "edit-recipe.html", form=form, recipe=recipe)

        set_form_dietary_tags(form, dietary_tag_bools_to_data(
            get_recipe_dietary_tags_bools(recipe)))

        form.ingredients.data = recipe.ingredients
        form.instructions.data = recipe.instructions

        if is_modified_recipe(recipe):
            form.extended_desc.data = recipe.extended_desc
            return render_template("edit-modified-recipe.html", form=form, recipe=recipe)
        else:
            form.title.data = recipe.title
            form.desc.data = recipe.desc
            form.image.data = recipe.image_url
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

    Retrieves the saved recipes associated with the current user.
    It then adds the 'created by' information to each recipe.

    Returns:
        Rendered template: The saved recipes page.
    """
    saved_recipes_keys = SavedRecipe.query.filter_by(
        user_id=current_user.id).all()

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
    if has_user_saved_recipe(current_user.id, recipe_id):
        saved_recipe = SavedRecipe.query.filter_by(
            user_id=current_user.id, recipe_id=recipe_id).first()
        db.session.delete(saved_recipe)
    else:
        saved_recipe = SavedRecipe(
            user_id=current_user.id, recipe_id=recipe_id)
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
    # Need to state no crsf token for search form
    # [https://stackoverflow.com/questions/61237524/validating-get-params-with-wtforms-in-flask]
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

        search_query = search_query.replace("+", " ")
        recipes = search_all_recipes(search_query, dietary_tags)

        add_created_by_to_recipes(recipes)
        search_form = SearchForm()
        dietary_tags = dietary_tag_data_to_names(dietary_tags)
        return render_template("search-results.html",
                               recipes=recipes, search_query=search_query,
                               dietary_tags=dietary_tags, search_form=search_form)
    # If doesn't validate, redirect to home with error message.
    recipes = get_all_recipes()
    add_created_by_to_recipes(recipes)
    return render_template("index.html",
                           recipes=recipes, search_form=search_form,
                           scroll="search-box")


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
