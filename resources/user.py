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

        
