"""
Association Rule Mining and Market Basket Analysis System
=========================================================
A professional capstone-quality web application for discovering
purchasing patterns using Apriori and FP-Growth algorithms.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CHARTS_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.dataset import dataset_bp
    from app.routes.preprocessing import preprocessing_bp
    from app.routes.eda import eda_bp
    from app.routes.mining import mining_bp
    from app.routes.rules import rules_bp
    from app.routes.visualization import visualization_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(eda_bp)
    app.register_blueprint(mining_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(visualization_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(reports_bp)

    # Create database tables
    with app.app_context():
        from app.models import User, Dataset, MiningResult
        db.create_all()
        # Create default admin user if not exists
        _create_default_admin()

    return app


def _create_default_admin():
    """Create default admin user"""
    from app.models import User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@system.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
