import traceback
from libs.mailgun import MailgunException
from blacklist import BLACKLIST
from models.user import UserModel
from flask_restful import Resource, request
from flask import make_response, render_template
from schemas.user import UserSchema

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
)

import hmac

NOT_FOUND_ERROR = "User not found."
ALREADY_EXISTS_ERROR = "User already exists."
DB_EXTRACTION_ERROR = "An error occurred '{}' user"
DELETED_MSG = "User deleted"
LOGOUT_MSG = "Successfully logged out."
INVALID_CREDS_ERROR_MSG = "Invalid creadentials"
CREATED_SUCCESSFULLY = "User created successfully, an email with an activation has been sent to your email."
NOT_ACTIVATED_ERROR = "User is not confirmed. Please, check email <{}>"
USER_CONFIRMED = "User confirmed."
EMAIL_ALREADY_EXISTS_ERROR = "Email already exists."
FAILED_TO_CREATE = "Failed to create user"

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            return {"message": ALREADY_EXISTS_ERROR}, 400

        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_ALREADY_EXISTS_ERROR}, 400
        try:
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": CREATED_SUCCESSFULLY}, 201
        except MailgunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": FAILED_TO_CREATE}, 500


class User(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        return user_schema.dump(user), 200

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
        user_json = request.get_json()
        user_data = user_schema.load(user_json)

        user = UserModel.find_by_username(user_data.username)

        if user and hmac.compare_digest(user.password, user_data.password):
            if user.is_activated:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)

                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": NOT_ACTIVATED_ERROR.format(user.email)}, 400
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


class UserActivate(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        
        user.is_activated = True
        user.save_to_db
        headers = {'Content-type': 'text/html'}
        return make_response(render_template('confirmation_page.html', email=user.email), 200, headers)