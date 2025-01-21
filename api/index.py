from app import app, db
from flask import request, jsonify

# This file is specifically for Vercel deployment
# It ensures the database is properly initialized

@app.route('/api/init-db', methods=['GET'])
def init_database():
    try:
        # Create all tables if they don't exist
        with app.app_context():
            db.create_all()
        return jsonify({"status": "Database initialized successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires a handler for the main route
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Database initialization endpoint'
    }

# Ensure the app can be imported and used by Vercel
__all__ = ['app', 'handler']
