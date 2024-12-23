from flask import Flask
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from backend.models import *
from backend.authentication import *
from flask_bcrypt import Bcrypt

app = None #initially none

def init_app():
    app = Flask(__name__) #object of Flask
    app.config["SECRET_KEY"] = "secret"
    from backend.controllers import controllers
    from backend.authentication import authentication

    #this part should be running after the Database is created

    login_manager = LoginManager()
    login_manager.login_view = 'authentication.user_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(controllers, url_prefix="/")
    app.register_blueprint(authentication, url_prefix="/")
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///application.sqlite3"
    app.app_context().push() #Direct access app by other modules(db, authentication)
    db.init_app(app) #object.method(<parameter>)
    # api.init_app(app)
    

    print("Application has started....")
    return app

    # from backend.models import *
    # from app import *
    # db.create_all()

app = init_app()
from backend.controllers import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()