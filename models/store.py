from db import db
from models.item import ItemJSON
from typing import List, Union, Dict

StoreJSON = Dict[str, Union[int, str, List[ItemJSON]]]
StoreJSONLIST = Dict[str, List[StoreJSON]]


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    items = db.relationship("ItemModel", lazy="dynamic")

    def __init__(self, name: str) -> None:
        self.name = name

    def json(self) -> StoreJSON:
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.json() for item in self.items.all()],
        }

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
    def get_store_list(cls) -> StoreJSONLIST:
        return {"stores": [store.json() for store in StoreModel.query.all()]}
