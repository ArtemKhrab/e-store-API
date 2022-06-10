from logging.config import valid_ident
import os
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from blacklist import BLACKLIST

from resources.item import Item, ItemsList
from resources.user import UserLogout, UserRegister, User, UserLogin, TokenRefresh
from resources.store import Store, StoreList
from ma import ma

from db import db


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("key")
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///data.db"
)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SQLALCHEMY_TRveCK_MODIFICATIONS"] = False
app.config["JWT_BLOCKLIST_ENABLE"] = True
app.config["JWT_BLOCKLIST_TOKEN_CHECKS"] = ["access", "refresh"]


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


@jwt.expired_token_loader
def exp_token_callback():
    return jsonify({"msg": "The token has expired.", "error": "token expired"}), 401


@jwt.token_in_blocklist_loader
def check_if_user_in_blacklist(*data):
    return data[1]["jti"] in BLACKLIST


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemsList, "/itemslist")
api.add_resource(UserRegister, "/register")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/storelist")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(debug=True)
