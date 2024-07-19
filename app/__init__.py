from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object('config')

    with app.app_context():
        from . import routes

    return app
