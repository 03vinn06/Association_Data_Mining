"""
Configuration for the Association Rule Mining System
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # PostgreSQL on Supabase
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase Storage
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_BUCKET = 'uploads'

    # Keep /tmp for charts (temporary is fine, charts are re-generated)
    UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
    REPORTS_FOLDER = os.path.join('/tmp', 'reports')
    CHARTS_FOLDER = os.path.join('/tmp', 'charts')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
