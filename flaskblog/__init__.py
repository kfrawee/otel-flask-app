from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# CONFIG
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# postgresql+psycopg2://[username]:[password]@[host]:[port]/[database]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:pwd@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

# db.init_app(app)


bcrypt = Bcrypt(app=app)
# Login manager
login_manager = LoginManager(app=app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


# routes
from flaskblog import routes
