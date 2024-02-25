from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import PasswordField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from myrecipe.routes import get_user, bcrypt
from myrecipe.models import User


class RegistrationForm(FlaskForm):
    """Flask form for user registration."""
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField(
        "Confirm your password:",
        validators=[DataRequired(), EqualTo("password")])

    def validate_username(self, username):
        """Raises a ValidationError if username is already taken."""
        if get_user(username.data):
            raise ValidationError(f"Username already taken: {username.data}")

class LoginForm(FlaskForm):
    """Flask form for loggin in"""
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=8, max=20)])

    def validate_username(self, username):
        """If username does not exist, raise ValidationError."""
        if not get_user(username.data):
            raise ValidationError(f"Username does not exist: {username.data}")
 
    def validate_password(self, password):
        """If password is wrong, raise ValidationError."""
        user = get_user(self.username.data)
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError("Password is incorrect.")
  
class AddRecipeForm(FlaskForm):
    """Flask form for adding a recipe."""
    title = StringField(
        "Title:",
        validators=[DataRequired(), Length(min=2, max=40)])
    desc = StringField(
        "Description:",
        validators=[DataRequired(), Length(min=2, max=200)])
    ingredients = TextAreaField(
        "Ingredients:",
        validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField(
        "Instructions:", validators=[DataRequired(), Length(min=10, max=1000)])
    image = FileField(
        "image",
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 
                                'Please only upload an image (jpg, png, or webp).')])

    # Dietary tags
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])
    
class AddModifiedRecipeForm(FlaskForm):
    """Flask form for adding a modified recipe."""
    extended_desc = StringField("Extended description:",
                                validators=[DataRequired(), Length(min=2, max=100)])
    ingredients = TextAreaField("Ingredients:",
                                validators=[DataRequired(), Length(min=10, max=500)])
    instructions = TextAreaField("Instructions:",
                                 validators=[DataRequired(), Length(min=10, max=1000)])

    # Dietary tags
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Vegetarian"), ("gf", "Gluten-free"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])

class SearchForm(FlaskForm):
    """Flask form for searching for a recipe"""
    search_bar = StringField("Search:")
     # Dietary tags
    dietary_tags = SelectMultipleField(choices=[("vv", "Vegan"), ("v", "Veggie"), ("gf", "GF"), ("df", "Dairy-free"), ("nf", "Nut-free"), ("ef", "Egg-free")])

    def validate_search_bar(self, search_bar):
        """If search bar is empty without any dietary filters applied, raise ValidationError."""
        if not search_bar.data and not self.dietary_tags.data:
            raise ValidationError("Please enter a search query or select a filter.")
        
class NewPasswordForm(FlaskForm):
    """Flask form for changing password.
    
    Used on the profile page."""
    current_password = PasswordField("Current password:", validators=[DataRequired(), Length(min=8, max=20)])
    new_password = PasswordField("New password:", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField("Confirm new password:", validators=[DataRequired(), EqualTo("new_password", "Passwords must match.")])

    def validate_current_password(self, current_password):
        """If current password is incorrect, raise ValidationError."""
        if not bcrypt.check_password_hash(User.query.get(current_user.id).password, self.current_password.data):
            raise ValidationError("Current password is incorrect.")
    
    def validate_confirm_password(self, new_password):
        """If new password value is not the same as the confirm password value, raise ValidationError."""
        if bcrypt.check_password_hash(User.query.get(current_user.id).password, self.new_password.data):
            raise ValidationError("New password cannot be the same as the current password.")