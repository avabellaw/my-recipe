from myrecipe import db
from sqlalchemy.orm import Mapped, mapped_column

class Users(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(25), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(), nullable=False)