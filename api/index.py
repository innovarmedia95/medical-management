from flask import Flask, request, jsonify, render_template
from app import app as application, db
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Wrap the main application for Vercel
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Medical Management Application'
    }

# Ensure routes are accessible
@application.route('/')
def index():
    return render_template('accueil.html')

# Database initialization endpoint
@application.route('/api/init-db', methods=['GET'])
def init_database():
    try:
        # Create all tables if they don't exist
        with application.app_context():
            db.create_all()
        return jsonify({"status": "Database initialized successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Make the application directly callable for Vercel
def app(environ, start_response):
    return application(environ, start_response)

# Expose the application for Vercel
__all__ = ['app', 'handler']
