"""
Configuration for the Association Rule Mining System
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key - set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database - use /tmp for Vercel (ephemeral), or DATABASE_URL env var for persistent DB
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('/tmp', 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads - /tmp is the only writable dir on Vercel
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join('/tmp', 'uploads')
    REPORTS_FOLDER = os.environ.get('REPORTS_FOLDER') or os.path.join('/tmp', 'reports')
    CHARTS_FOLDER = os.environ.get('CHARTS_FOLDER') or os.path.join('/tmp', 'charts')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
