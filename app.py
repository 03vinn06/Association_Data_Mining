"""
==========================================================================
Association Rule Mining and Market Basket Analysis System
==========================================================================
Using Apriori and FP-Growth Algorithm

Run this file to start the web application:
    python run.py

Then open your browser to: http://127.0.0.1:5000

Default Login:
    Username: admin
    Password: admin123
==========================================================================
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  ARM System - Market Basket Analysis")
    print("  Starting server at http://127.0.0.1:5000")
    print("  Login: admin / admin123")
    print("=" * 60)
    app.run(debug=True)
