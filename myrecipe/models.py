from flask_login import UserMixin
from myrecipe import db


class User(db.Model, UserMixin):
    """Represents a user in SQL.

    Attributes:
        id (int): Primary key.
        username (str)
        password (str)
        user_type (str): Type/role of user (e.g., admin, standard user).
        
        recipes (relationship): Recipes created by user.
        saved_recipes (relationship): Users saved recipes.
        modified_recipes (relationship): Modified recipes created by user

    Methods:
        __repr__(str): Returns string representation of user.
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete")
    saved_recipes = db.relationship(
        "SavedRecipe", backref="user", cascade="all, delete")
    modified_recipes = db.relationship(
        "ModifiedRecipe", backref="user", cascade="all, delete")

    def __repr__(self):
        return f"User {self.id} - {self.username}"


class Recipe(db.Model):
    """Represents a recipe in SQL.

    Attributes:
        id (int): Recipe primary key.
        user_id (int): Foreign key - the user who created the recipe.
        title (str): Recipe title.
        desc (str): Recipe description.
        ingredients (str): Recipe ingredients.
        instructions (str): Recipe instructions.
        image_url (str): Recipe image URL.
        dietary_tags_id (int): Foreign key - the recipe's dietary tags.
        
        saved_recipes (relationship): SavedRecipe entries associated with the recipe.
        recipe_copies (relationship): Modified recipes based on the recipe.
        dietary_tags (relationship): DietaryTags associated with the recipe.

    Methods:
        __repr__(str): Returns a string representation of the recipe.
    """
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    dietary_tags_id = db.Column(db.Integer, db.ForeignKey(
        "dietary_tags.id"), nullable=False)

    saved_recipes = db.relationship(
        "SavedRecipe", backref="recipe", cascade="all, delete")
    recipe_copies = db.relationship(
        "ModifiedRecipe", backref="original_recipe", cascade="all, delete")

    dietary_tags = db.relationship(
        "DietaryTags", backref="recipe", cascade="all, delete")

    def __repr__(self):
        return f"{self.title} [ID: {self.id}]"


class ModifiedRecipe(db.Model):
    """Represents a modified recipe in SQL.

    Attributes:
        id (int): Primary key
        modified_by_id (int): Foreign key - the user who created the modified recipe.
        recipe_id (int): Foreign key - the original recipe.
        extended_desc (str): Recipe extended description.
        ingredients (str): The modified ingredients.
        instructions (str): The modified instructions.
        dietary_tags_id (int): Foreign key - The modified recipe's dietary tags.
        dietary_tags (relationship): DietaryTags associated with the recipe.

    Methods:
        __repr__(str): Returns a string representation of the modified recipe.
    """
    __tablename__ = "modified_recipes"
    id = db.Column(db.Integer, primary_key=True)
    modified_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False)

    recipe_id = db.Column(db.Integer, db.ForeignKey(
        "recipes.id"), nullable=False)

    extended_desc = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    dietary_tags_id = db.Column(db.Integer, db.ForeignKey(
        "dietary_tags.id"), nullable=False)

    dietary_tags = db.relationship(
        "DietaryTags", backref="modified_recipe", cascade="all, delete")

    def __repr__(self):
        return f'{self.original_recipe.title} (Modified recipe) [ID: {self.id}]'


class DietaryTags(db.Model):
    """Represents dietary tags in SQL.
    
    To be associated with a recipe.

    Attributes:
        id (int): Primary key.
        is_vegan (bool): True if the recipe is vegan.
        is_vegetarian (bool): True if the recipe is vegetarian.
        is_gluten_free (bool): True if the recipe is gluten-free.
        is_dairy_free (bool): True if the recipe is dairy-free.
        is_nut_free (bool): True if the recipe is nut-free.
        is_egg_free (bool): True if the recipe is egg-free.
    """

    __tablename__ = "dietary_tags"
    id = db.Column(db.Integer, primary_key=True)
    is_vegan = db.Column(db.Boolean, nullable=False)
    is_vegetarian = db.Column(db.Boolean, nullable=False)
    is_gluten_free = db.Column(db.Boolean, nullable=False)
    is_dairy_free = db.Column(db.Boolean, nullable=False)
    is_nut_free = db.Column(db.Boolean, nullable=False)
    is_egg_free = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return (f"dietary tags - vv:{self.is_vegan}"
                + "veg:{self.is_vegetarian},"
                + "g:{self.is_gluten_free},"
                + "d:{self.is_dairy_free},"
                + "n:{self.is_nut_free},"
                + "e:{self.is_egg_free}")


class SavedRecipe(db.Model):
    """Represents a saved recipe.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key - the user who saved the recipe.
        recipe_id (int): Foreign key - the recipe that's saved.
    """
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(
        "recipes.id"), nullable=False)
