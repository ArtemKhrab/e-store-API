from time import time
import traceback

from flask import make_response, render_template
from flask_restful import Resource
from libs.mailgun import MailgunException

from models.user import UserModel
from resources.user import NOT_FOUND_ERROR
from models.confirmation import ConfirmationModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()

NOT_FOUND = "Current confirmation email is not found."
EXPIRED = "Confirmation email expired."
ALREADY_CONFIRTMED = "The account is already confirmed."
RESEND_SUCCESSFUL = "Email was successfuly resent."
RESEND_FAIL = "A resend failed."

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired():
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRTMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email), 
            200, 
            headers
        )
    
class ConfriamtionByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )
    
    @classmethod
    def post(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND_ERROR}, 404
        
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRTMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFUL}
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAIL}, 500