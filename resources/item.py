from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt
from models.item import ItemModel
from schemas.item import ItemSchema


NOT_FOUND_ERROR = "Item not found."
ALREADY_EXISTS_ERROR = "Item already exists."
DB_EXTRACTION_ERROR = "An error occurred '{}' item"
DELETED_MSG = "Item deleted"

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required()
    def get(cls, name: str):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        if item:
            return item_schema.dump(item), 200
        else:
            return {"message": NOT_FOUND_ERROR}, 404

    @classmethod
    @jwt_required(fresh=True)
    def post(cls, name: str):
        try:
            if ItemModel.find_by_name(name):
                return {"message": ALREADY_EXISTS_ERROR}, 400
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        item_json = request.get_json()
        item_json["name"] = name
        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": DB_EXTRACTION_ERROR.format("inserting")}, 500

        return item_schema.dump(item), 201

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
        item_json = request.get_json()

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name
            item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": DB_EXTRACTION_ERROR.format("saving")}, 500

        return item_schema.dump(item), 200


class ItemsList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            return {"items": item_list_schema.dump(ItemModel.get_all())}, 200
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting") + "list"}, 500
