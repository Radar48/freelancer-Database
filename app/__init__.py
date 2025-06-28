from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from typing import List, Dict

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///freelancer_income_tracker.db"
    app.config["SECRET_KEY"] = "your-secret-key"

    db.init_app(app)  # critical!
    login_manager.init_app(app)
    login_manager.login_view = 'login' 

    from app.models import User  # Must import after db.init_app()
    from app.routes import routes 
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app