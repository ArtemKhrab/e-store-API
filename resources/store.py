from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.store import StoreModel

NOT_FOUND_ERROR = "Store not found."
ALREADY_EXISTS_ERROR = "Store already exists."
DB_EXTRACTION_ERROR = "An error occurred '{}' store"
DELETED_MSG = "Store deleted."


class Store(Resource):
    @classmethod
    @jwt_required()
    def get(cls, name: str):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        if store:
            return store.json(), 200
        else:
            return {"message": NOT_FOUND_ERROR}, 404

    @classmethod
    @jwt_required()
    def post(cls, name: str):
        try:
            if StoreModel.find_by_name(name):
                return {"message": ALREADY_EXISTS_ERROR}, 400
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting")}, 500

        store = StoreModel(name)

        try:
            store.save_to_db()
            return store.json(), 201
        except:
            return {"message": DB_EXTRACTION_ERROR.format("saving")}, 500

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            try:
                store.delete_from_db()
            except:
                return {"message": DB_EXTRACTION_ERROR.format("deleting")}, 500
        return {"message": DELETED_MSG}, 200


class StoreList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            return StoreModel.get_store_list(), 200
        except:
            return {"message": DB_EXTRACTION_ERROR.format("getting") + "list"}, 500
