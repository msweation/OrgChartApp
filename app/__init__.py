from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils import download_from_gcs

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from . import routes, auth
        app.register_blueprint(auth.auth, url_prefix='/auth')
        db.create_all()

        # Download org_chart.json on app load
        local_json_path = app.config['LOCAL_JSON_PATH']
        download_from_gcs('org_chart.json', local_json_path)

    return app