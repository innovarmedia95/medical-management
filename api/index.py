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
    from flask import Flask, request, jsonify, render_template
    from app import app as application, db
except Exception as import_error:
    logger.error(f"Import Error: {import_error}")
    logger.error(traceback.format_exc())
    raise

# Wrap the main application for Vercel with error handling
def handler(event, context):
    try:
        return {
            'statusCode': 200,
            'body': 'Medical Management Application'
        }
    except Exception as e:
        logger.error(f"Handler Error: {e}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': f'Application Error: {str(e)}'
        }

# Ensure routes are accessible with error handling
@application.route('/')
def index():
    try:
        return render_template('accueil.html')
    except Exception as e:
        logger.error(f"Index Route Error: {e}")
        logger.error(traceback.format_exc())
        return f"Error rendering page: {str(e)}", 500

# Database initialization endpoint
@application.route('/api/init-db', methods=['GET'])
def init_database():
    try:
        # Create all tables if they don't exist
        with application.app_context():
            db.create_all()
        return jsonify({"status": "Database initialized successfully"}), 200
    except Exception as e:
        logger.error(f"Database Initialization Error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Make the application directly callable for Vercel
def app(environ, start_response):
    try:
        return application(environ, start_response)
    except Exception as e:
        logger.error(f"WSGI Application Error: {e}")
        logger.error(traceback.format_exc())
        # Implement a basic error response
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'An error occurred while processing the request']

# Expose the application for Vercel
__all__ = ['app', 'handler']

# Log startup
logger.info("Vercel deployment configuration loaded successfully")
