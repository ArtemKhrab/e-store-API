import os
from tkinter.tix import Tree
from traceback import print_tb
from dotenv import load_dotenv
 
from flask import Flask, jsonify
from flask_restful import Api 
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST
from models.user import UserModel

from resources.item import Item, ItemsList
from resources.user import UserLogout, UserRegister, User, UserLogin, TokenRefresh
from resources.store import Store, StoreList


from db import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("key")
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_BLOCKLIST_ENABLE'] = True 
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if UserModel.find_by_id(identity).is_admin:
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def exp_token_callback():
    return jsonify({
        'msg': 'The token has expired.',
        'error': 'token expired'
    }), 401 

@jwt.token_in_blocklist_loader
def check_if_user_in_blacklist(*data):
    return data[1]['jti'] in BLACKLIST

    
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemsList, '/itemslist')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/storelist')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True)
    

