from blacklist import BLACKLIST
from models.user import UserModel
from flask_restful import Resource, reqparse, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
)
import hmac

BLANK_ERROR = "'{}' cannot be left blank!"
NOT_FOUND_ERROR = "User not found."
ALREADY_EXISTS_ERROR = "User already exists."
DB_EXTRACTION_ERROR = "An error occurred '{}' user"
DELETED_MSG = "User deleted"
LOGOUT_MSG = "Successfully logged out."
INVALID_CREDS_ERROR_MSG = "Invalid creadentials"
CREATED_SUCCESSFULLY = "User created successfully"

parser = reqparse.RequestParser()
parser.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username")
)

parser.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password")
)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        request_data = parser.parse_args()

        if UserModel.find_by_username(request_data["username"]):
            return {"message": ALREADY_EXISTS_ERROR}, 400
        user = UserModel(**request_data)
        try:
            user.save_to_db()
            return {"message": CREATED_SUCCESSFULLY}, 201
        except:
            return {"message": DB_EXTRACTION_ERROR.format("creating")}, 500


class User(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        user.delete_from_db()
        return {"message": DELETED_MSG}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = parser.parse_args()
        user = UserModel.find_by_username(data["username"])
        if user and hmac.compare_digest(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDS_ERROR_MSG}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]
        print(get_jwt()["jti"])
        BLACKLIST.add(jti)
        return {"message": LOGOUT_MSG}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        if get_jwt()["jti"] in BLACKLIST:
            return {"msg": "Token has been revoked"}
        cur_user = get_jwt()["sub"]
        new_token = create_access_token(identity=cur_user, fresh=False)
        return {"access_token": new_token}, 200
