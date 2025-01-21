import sys
import os
import traceback
import logging

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

try:
    from flask import Flask, request, jsonify
    from app import app, db
except Exception as import_error:
    logger.error(f"Import Error: {import_error}")
    logger.error(traceback.format_exc())
    raise

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
def app(environ, start_response):
    return app(environ, start_response)

__all__ = ['app', 'handler']

# Log startup
logger.info("Vercel deployment configuration loaded successfully")
