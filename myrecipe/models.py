from email.mime import image
from myrecipe import db
from flask_login import UserMixin  

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    
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
    image_url = db.Column(db.String(100), nullable=True)
    
    saved_recipes = db.relationship("SavedRecipe", backref="recipe", cascade="all, delete")
    recipe_copies = db.relationship("ModifiedRecipe", backref="original_recipe", cascade="all, delete")
    
    def __repr__(self):
        return f"{self.id} -{self.title}"
    
class ModifiedRecipe(db.Model):
    __tablename__ = "modified_recipes"
    id = db.Column(db.Integer, primary_key=True)
    modified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    
    def __repr__(self):
        return f"[ID: {self.id}] - Modified from [ID: {self.recipe_id}]"
    
class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)