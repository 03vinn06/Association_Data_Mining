"""
WSGI entry point for Vercel and other WSGI servers
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)
