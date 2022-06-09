from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from models.item import ItemModel

BLANK_ERROR = "'{}' cannot be left blank!"
NOT_FOUND_ERROR = "Item not found."
ALREADY_EXISTS_ERROR = "Item already exists."
DB_EXTRACTION_ERROR = "An error occurred '{}' item"
DELETED_MSG = "Item deleted"

parser = reqparse.RequestParser()
parser.add_argument(
    "price", type=float, required=True, help=BLANK_ERROR.format("price")
)

parser.add_argument(
    "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
)


class Item(Resource):
    @classmethod
    @jwt_required()
    def get(cls, name: str):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        if item:
            return item.json(), 200
        else:
            return {"message": NOT_FOUND_ERROR}, 404

    @classmethod
    @jwt_required(fresh=True)
    def post(cls, name: str):
        requested_data = parser.parse_args()
        try:
            if ItemModel.find_by_name(name):
                return {"message": ALREADY_EXISTS_ERROR}, 400
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        item = ItemModel(name, **requested_data)

        try:
            item.save_to_db()
        except:
            return {"message": DB_EXTRACTION_ERROR.format("inserting")}, 500

        return item.json(), 201

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            try:
                item.delete_from_db()
            except:
                return {"message": DB_EXTRACTION_ERROR.format("deleting")}, 500
        return {"message": DELETED_MSG}

    @classmethod
    @jwt_required()
    def put(cls, name: str):
        requested_data = parser.parse_args()

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        if item is None:
            item = ItemModel(name, **requested_data)
        else:
            item.price = requested_data["price"]

        try:
            item.save_to_db()
        except:
            return {"message": DB_EXTRACTION_ERROR.format("saving")}, 500

        return item.json(), 200


class ItemsList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            return ItemModel.get_items_list(), 200
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting") + "list"}, 500
