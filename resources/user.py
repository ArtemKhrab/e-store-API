from blacklist import BLACKLIST
from models.user import UserModel
from flask_restful import Resource, reqparse, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
import hmac

parser = reqparse.RequestParser()
parser.add_argument('username', 
    type=str, 
    required=True,
    help="This field cannot be left blank!")

parser.add_argument('password', 
    type=str, 
    required=True,
    help="This field cannot be left blank!")

class UserRegister(Resource):
    def post(self):
        request_data = parser.parse_args()

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
    @jwt_required()
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


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data =  parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and hmac.compare_digest(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {'message': 'Invalid creadentials'}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        print(get_jwt()['jti'])
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'},


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        print(get_jwt()['jti'])
        if get_jwt()['jti'] in BLACKLIST:
            return {'msg': 'Token has been revoked'}
        cur_user = get_jwt()['sub']
        new_token = create_access_token(identity=cur_user, fresh=False)
        return {'access_token': new_token}, 200