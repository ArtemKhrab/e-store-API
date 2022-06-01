from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', 
        type=float, 
        required=True,
        help="This field cannot be left blank!")

    parser.add_argument('store_id', 
        type=int, 
        required=True,
        help="This field cannot be left blank!")

    @jwt_required()
    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": "An error occurred getting the item."}, 500

        if item:
            return item.json(), 200
        else:
            return {"message": "Item not found."}, 404

    
    @jwt_required()
    def post(self, name):
        requested_data = self.parser.parse_args()
        try:
            if ItemModel.find_by_name(name):
                return {"message": "Item already exists."}, 400
        except:
             return {"message": "An error occurred getting the item."}, 500

        item = ItemModel(name, **requested_data)

        try:
            item.save_to_db() 
        except:
            return {"message": "An error occurred inserting the item."}, 500 

        return item.json(), 201
    
    @jwt_required()
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            try:
                item.delete_from_db()
            except:
                return {"message": "An error occurred deleting the item."}, 500
        return {'message': 'Item deleted.'}
    
    @jwt_required()
    def put(self, name):
        requested_data = self.parser.parse_args()

        try:
            item = ItemModel.find_by_name(name)      
        except:      
            return {"message": "An error occurred getting the item."}, 500

        if item is None:
            item = ItemModel(name, **requested_data)
        else:
            item.price = requested_data["price"]
            # item.price = requested_data["store_id"]
        
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred saving the item."}, 500

        return item.json(), 200


class ItemsList(Resource):

    @jwt_required()
    def get(self):
        try:
           return ItemModel.get_items_list(), 200
        except:
            return {"message": "An error occurred getting the items list."}, 500

