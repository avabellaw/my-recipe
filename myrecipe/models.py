from email.mime import image
from myrecipe import db
from flask_login import UserMixin  

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    
    def __repr__(self):
        return f"User {self.id} - {self.username}"
    
class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f"{self.title} [ID: {self.id}]"
    
class SavedRecipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)