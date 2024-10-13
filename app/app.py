from flask import Flask
from main.controller.solarController import solar_bp

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    # hook app with controllers
    app.register_blueprint(solar_bp)
    return app

if __name__=="__main__":
    app = create_app()
    app.run()
