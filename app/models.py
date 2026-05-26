"""
Database Models for the Association Rule Mining System
"""
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    datasets = db.relationship('Dataset', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Dataset(db.Model):
    """Uploaded dataset model"""
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    total_transactions = db.Column(db.Integer, default=0)
    total_items = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_preprocessed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    mining_results = db.relationship('MiningResult', backref='dataset', lazy=True)

    def __repr__(self):
        return f'<Dataset {self.name}>'


class MiningResult(db.Model):
    """Mining results model"""
    __tablename__ = 'mining_results'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)  # 'apriori' or 'fpgrowth'
    min_support = db.Column(db.Float, nullable=False)
    min_confidence = db.Column(db.Float, nullable=False)
    min_lift = db.Column(db.Float, default=1.0)
    num_frequent_itemsets = db.Column(db.Integer, default=0)
    num_rules = db.Column(db.Integer, default=0)
    frequent_itemsets_json = db.Column(db.Text)
    rules_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MiningResult {self.algorithm} - Dataset {self.dataset_id}>'


class ActivityLog(db.Model):
    """User activity log"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activities')

    def __repr__(self):
        return f'<ActivityLog {self.action}>'
