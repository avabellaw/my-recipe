from flask_login import UserMixin  
from myrecipe import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    
    recipes = db.relationship("Recipe", backref="user", cascade="all, delete")
    saved_recipes = db.relationship("SavedRecipe", backref="user", cascade="all, delete")
    modified_recipes = db.relationship("ModifiedRecipe", backref="user", cascade="all, delete")
    
    def __repr__(self):
        return f"User {self.id} - {self.username}"
    
class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    dietary_tags_id = db.Column(db.Integer, db.ForeignKey("dietary_tags.id"), nullable=False)
    
    saved_recipes = db.relationship("SavedRecipe", backref="recipe", cascade="all, delete")
    recipe_copies = db.relationship("ModifiedRecipe", backref="original_recipe", cascade="all, delete")
    
    dietary_tags = db.relationship("DietaryTags", backref="recipe", cascade="all, delete")
    
    def __repr__(self):
        return f"{self.title} [ID: {self.id}]"
    
class ModifiedRecipe(db.Model):
    __tablename__ = "modified_recipes"
    id = db.Column(db.Integer, primary_key=True)
    modified_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    extended_desc = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    dietary_tags_id = db.Column(db.Integer, db.ForeignKey("dietary_tags.id"), nullable=False)
    
    dietary_tags = db.relationship("DietaryTags", backref="modified_recipe", cascade="all, delete")
    
    def __repr__(self):
        return f'{self.original_recipe.title} (Modified recipe) [ID: {self.id}]' # type: ignore
    
class DietaryTags(db.Model):
    __tablename__ = "dietary_tags"
    id = db.Column(db.Integer, primary_key=True)
    is_vegan = db.Column(db.Boolean, nullable=False)
    is_vegetarian = db.Column(db.Boolean, nullable=False)
    is_gluten_free = db.Column(db.Boolean, nullable=False)
    is_dairy_free = db.Column(db.Boolean, nullable=False)
    is_nut_free = db.Column(db.Boolean, nullable=False)
    is_egg_free = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f"dietary tags - vv:{self.is_vegan}, veg:{self.is_vegetarian}, g:{self.is_gluten_free}, d:{self.is_dairy_free}, n:{self.is_nut_free}, e:{self.is_egg_free} " # type: ignore
    
class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)