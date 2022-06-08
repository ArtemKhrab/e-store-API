from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.store import StoreModel


class Store(Resource):
    @jwt_required()
    def get(self, name):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {"message": "An error occurred getting the store."}, 500

        if store:
            return store.json(), 200
        else:
            return {"message": "Store not found."}, 404
        
    @jwt_required()
    def post(self, name):
        try:
            if StoreModel.find_by_name(name):
                return {"message": "Store already exists."}, 400
        except:
            return {"message": "An error occurred getting the store."}, 500 

        store = StoreModel(name)

        try:
            store.save_to_db()
            return store.json(), 201
        except:
            return {"message": "An error occurred saving the store."}, 500 

    @jwt_required()
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            try:
                store.delete_from_db()
            except:
                return {"message": "An error occurred deleting the store."}, 500
        return {'message': 'Store deleted.'}, 200


class StoreList(Resource):
    
    @jwt_required()
    def get(self):
        try:
           return StoreModel.get_store_list(), 200
        except:
            return {"message": "An error occurred getting the store list."}, 500
