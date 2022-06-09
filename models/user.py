from db import db
from typing import Dict, Union

UserJSON = Dict[str, Union[int, str, bool]]


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def json(self) -> UserJSON:
        return {"id": self.id, "username": self.username, "admin": self.is_admin}

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
