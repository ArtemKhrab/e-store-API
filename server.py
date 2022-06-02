import os

from flask import Flask
from flask_restful import Api 
from flask_jwt import JWT


from resources.item import Item, ItemsList
from resources.user import UserRegister
from resources.store import Store, StoreList

from security import auth, identity
from db import db

app = Flask(__name__)
app.secret_key = "asfA13nQJSdp12nASdjqsdl39rasjSd2"
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWT(app, auth, identity)  #  /auth
    
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemsList, '/itemslist')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/storelist')

if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True)
    

