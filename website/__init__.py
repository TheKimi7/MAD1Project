from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "dbase.db"
UPLOAD_FOLDER = 'website\static'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_NAME
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    create_database(app)

    from .models import user, post
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    login_manager.login_message = 'You Must Login to Access the Blog!'

    @login_manager.user_loader
    def load_user(id):
        return user.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Database Created!")