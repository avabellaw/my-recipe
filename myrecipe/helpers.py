"""
Contains all the functions used by routes in My Recipe.
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from myrecipe.models import DietaryTags, User, Recipe, SavedRecipe, ModifiedRecipe
from myrecipe import app, db, UserType, DIETARY_TAGS

def get_user(username):
    """Retrieve user from database using their username.

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
        m_recipe.modified_by = User.query.filter_by(
            id=m_recipe.modified_by_id).first().username


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
    dietary_tags = DietaryTags(is_vegan="vv" in form_dietary_tags,
                               is_vegetarian="v" in form_dietary_tags,
                               is_gluten_free="gf" in form_dietary_tags,
                               is_dairy_free="df" in form_dietary_tags,
                               is_nut_free="nf" in form_dietary_tags,
                               is_egg_free="ef" in form_dietary_tags)
    db.session.add(dietary_tags)
    db.session.commit()
    return dietary_tags.id


def add_created_by_to_recipes(recipes):
    """Adds the created_by attribute to the recipes

    Args:
        recipes (list): The recipes to add the created_by attribute to.
    """
    for recipe in recipes:
        user_id = recipe.original_recipe.user_id if is_modified_recipe(
            recipe) else recipe.user_id
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
    result = cloudinary.uploader.upload(
        image, public_id=image.filename, folder="myrecipe/image-uploads")
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
    # If file with same name exists, add a number to the end of the filename.
    # Increment until a unique filename is found
    while os.path.isfile(os.path.join(save_path, filename)):
        filename_parts = filename.split(".")
        filename_name = filename_parts[0]
        if "_" in filename_name:
            filename_name = filename_name.split("_")[0] + f"_{counter}"
        else:
            filename_name = filename_name + "_2"
        filename = f'{filename_name}.{".".join(filename_parts[1:])}'
        counter += 1

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
        return recipe.modified_by_id == user_id
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
    recipes = Recipe.query.filter(
        Recipe.title.ilike(f"%{search_query}%")).all()
    recipes.extend(Recipe.query.filter(
        Recipe.desc.ilike(f"%{search_query}%")).all())

    # Get all modified recipes that match the search query
    modified_recipes = ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(
        Recipe.title.ilike(f"%{search_query}%")).all() 
    modified_recipes.extend(ModifiedRecipe.query.join(ModifiedRecipe.original_recipe).filter(
        Recipe.desc.ilike(f"%{search_query}%")).all())
    add_recipe_data_to_modified_recipes(modified_recipes)

    # Extend recipes with modified recipes
    recipes.extend(modified_recipes)
    recipes = set(recipes)  # Remove duplicates

    # Create dietary tags boolean filter
    add_dietary_tags_to_recipes(recipes)
    dietary_tags_filter = dietary_tag_data_to_bools(args[0])

    # Apply dietary tags filter
    if True in dietary_tags_filter:
        filtered_recipes = []
        for recipe in recipes:
            recipe_filter = get_recipe_dietary_tags_bools(recipe)
            passed = [recipe_filter[i] for i in range(
                len(dietary_tags_filter)) if dietary_tags_filter[i]]

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
    """Adds dietary tags to a list of recipes.

    Also sets whether the recipe has dietary tags or not.

    Args:
        recipes (list): List of recipes.
    """
    for recipe in recipes:
        tags = DietaryTags.query.filter_by(id=recipe.dietary_tags_id).first()
        if tags:
            recipe.is_vegan = tags.is_vegan
            recipe.is_vegetarian = tags.is_vegetarian
            recipe.is_gluten_free = tags.is_gluten_free
            recipe.is_dairy_free = tags.is_dairy_free
            recipe.is_nut_free = tags.is_nut_free
            recipe.is_egg_free = tags.is_egg_free

            recipe.has_dietary_tags = any([recipe.is_vegan,
                                           recipe.is_vegetarian,
                                           recipe.is_gluten_free,
                                           recipe.is_dairy_free,
                                           recipe.is_nut_free,
                                           recipe.is_egg_free])
        else:
            recipe.has_dietary_tags = False


def dietary_tag_data_to_bools(dietary_tags):
    """Converts dietary tag data from the select fields into boolean values."""
    return [tag in dietary_tags for tag in DIETARY_TAGS]


def dietary_tag_data_to_names(dietary_tags):
    """Converts dietary tag data from select fields into humane-readable names.

    Args:
        dietary_tags (list): A list of dietary tag data.

    Returns:
        list: The dietary tag names from the data.
    """
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
    """Returns the dietary tag data from the boolean values.

    This can be used to set the default values of the dietary tags.
    This is from the dietary tags select field.
    """
    return [tag for tag in DIETARY_TAGS
            if dietary_tags[DIETARY_TAGS.index(tag)]]


def get_recipe_dietary_tags_bools(recipe):
    """Returns a list of booleans from the dietary tags of a recipe."""
    return [recipe.is_vegan,
            recipe.is_vegetarian,
            recipe.is_gluten_free,
            recipe.is_dairy_free,
            recipe.is_nut_free,
            recipe.is_egg_free]


def is_modified_recipe(recipe):
    """Returns bool: True if the recipe is a modified recipe else false."""
    return hasattr(recipe, "original_recipe")


def update_recipe(recipe, title, desc, ingredients, instructions, image):
    """Update the recipe with the new proposed new version.

    Checks whether the data has changed before updating.

    Args:
        recipe (Recipe): The recipe to be updated.
        title (str): The title form data.
        desc (str): The description form data
        ingredients (str): The ingrediends form data.
        instructions (str): The instructions form data.
        image (FileStorage): The image file form data.
    """
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
    """Update the modified recipe with the proposed new version.

    Checks whether the data has changed before updating.

    Args:
        recipe (Recipe): The recipe to be updated.
        ingredients (str): The ingrediends form data.
        instructions (str): The instructions form data.
        extended_desc (str): The extended description form data.
    """
    if extended_desc != recipe.extended_desc:
        recipe.extended_desc = extended_desc
    if ingredients != recipe.ingredients:
        recipe.ingredients = ingredients
    if instructions != recipe.instructions:
        recipe.instructions = instructions
    db.session.add(recipe)
    db.session.commit()


def update_dietary_tags(recipe, new_dietary_tags_data):
    """Update the dietary tags of a recipe in the db with proposed new version.

    Checks whether the data is different to what's already in the db before updating.

    Args:
        recipe (Recipe): The recipe object to update the dietary tags for.
        new_dietary_tags_data (str): The new dietary tags data to update the recipe with.

    """
    dietary_tags = DietaryTags.query.get(recipe.dietary_tags_id)
    dietart_tag_data = dietary_tag_bools_to_data(
        get_recipe_dietary_tags_bools(recipe))
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
    """Check if the user is an admin.

    Args:
        user_id (int): The ID of the user to check.

    Returns:
        bool: True if the user is an admin else false.
    """

    return User.query.filter_by(id=user_id,
                                user_type=UserType.ADMIN.value).first() is not None
