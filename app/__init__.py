from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    with app.app_context():
        from . import routes
        
    print(f"Configured templates folder: {app.template_folder}")
    print(f"Configured static folder: {app.static_folder}")
    
    return app
