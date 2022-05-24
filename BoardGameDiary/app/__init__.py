from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config['MONGO_URI'] = "mongodb+srv://admin:admin@mock.q2gii.mongodb.net/test"
    app.config['DEBUG'] = 1
    app.config['SECRET_KEY'] = "authenticationMicroserviceTest"

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app