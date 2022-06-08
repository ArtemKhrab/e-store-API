from models.user import UserModel
from flask_restful import Resource, reqparse, request
 
class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', 
        type=str, 
        required=True,
        help="This field cannot be left blank!")
    parser.add_argument('password', 
        type=str, 
        required=True,
        help="This field cannot be left blank!")

    def post(self):
        request_data = self.parser.parse_args()

        if UserModel.find_by_username(request_data["username"]):
            return {"message": "Username already exists"}, 400
        user = UserModel(**request_data)
        try:
            user.save_to_db()
            return {"message": "User created successfully"}, 201
        except Exception as ex:
            return {"message": "An error occurred creating the user."}, 500

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': "User not found"}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': "User not found"}, 404
        user.delete_from_db()
        return {'message': 'User deleted'}, 200

        
