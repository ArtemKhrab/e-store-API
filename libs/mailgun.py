from typing import List
from requests import Response, post
import os

FAILED_LOAD_API_KEY = "Failed to load MAILGUN_API_KEY"
FAILED_LOAD_DAMAIN = "Failed to load MAILGUN_DOMAIN"
ERROR_SENDING_EMAIL = "Error in sending confirmation email, user registration failed"


class MailgunException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_TITLE = "Mailgun Sandbox"
    FROM_EMAIL = "postmaster@sandbox6920922dd18e4736bc90a41e1d8a0ea9.mailgun.org"

    def send_email(self, email: List[str], subject: str, text: str, html: str) -> Response:
        if self.MAILGUN_API_KEY is None:
            raise MailgunException(FAILED_LOAD_API_KEY)
        if self.MAILGUN_DOMAIN is None:
            raise MailgunException(FAILED_LOAD_DAMAIN)

        response = post(
            f"https://api.mailgun.net/v3/{self.MAILGUN_DOMAIN}/messages",
                auth=("api", self.MAILGUN_API_KEY),
                data={
                    "from": f"{self.FROM_TITLE} <{self.FROM_EMAIL}>",
                    "to": email,
                    "subject": subject,
                    "text": text,
                    "html": html,
                },
        )

        if response.status_code != 200:
            raise MailgunException(ERROR_SENDING_EMAIL)

        return response