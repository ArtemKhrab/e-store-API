from db import db
from typing import List


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    items = db.relationship("ItemModel", lazy="dynamic")

    def __init__(self, name: str) -> None:
        self.name = name

    @classmethod
    def find_by_name(cls, name: str) -> "StoreModel":
        return cls.query.filter_by(name=name).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls) -> List["StoreModel"]:
        return cls.query.all()
