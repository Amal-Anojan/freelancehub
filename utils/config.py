from dotenv import load_dotenv
import os

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

class Config:
    SECRET_KEY = "'56ee6ec2d9da0a4ffdd6bcb90809def3'"
    SQLALCHEMY_DATABASE_URI =  "mysql://root:amal6230/.#@localhost/freelancehub1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings (use your SMTP server or Gmail with App Password)
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = "amaloff7@gmail.com"
    MAIL_PASSWORD = "" 
    MAIL_DEFAULT_SENDER = "noreply@freelancehub.com"
