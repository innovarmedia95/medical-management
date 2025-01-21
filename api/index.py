import sys
import os
import traceback
import logging

# Configure logging to write to a file
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'vercel_deployment.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure project root is in Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Detailed import logging
try:
    import flask
    import sqlalchemy
    from app import app as application, db
    import jinja2
except Exception as import_error:
    logger.error("CRITICAL IMPORT ERROR")
    logger.error(f"Import Error Details: {import_error}")
    logger.error(f"Python Path: {sys.path}")
    logger.error(f"Current Working Directory: {os.getcwd()}")
    logger.error(traceback.format_exc())
    raise

def log_system_info():
    """Log system and environment information"""
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Flask Version: {flask.__version__}")
    logger.info(f"SQLAlchemy Version: {sqlalchemy.__version__}")
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Environment Variables: {os.environ}")

# Log system information on startup
log_system_info()

# This file is specifically for Vercel deployment
# It ensures the database is properly initialized

# Wrap the main application for Vercel with error handling
def handler(event, context):
    """Vercel serverless function handler with comprehensive error tracking"""
    try:
        logger.info("Vercel handler invoked")
        return {
            'statusCode': 200,
            'body': 'Database initialization endpoint'
        }
    except Exception as e:
        logger.error("CRITICAL: Handler failed")
        logger.error(f"Handler Error: {e}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': f'Application Error: {str(e)}'
        }

@application.route('/')
def index():
    try:
        return application.render_template('accueil.html')
    except Exception as e:
        logger.error(f"Index Route Error: {e}")
        logger.error(traceback.format_exc())
        return f"Error rendering page: {str(e)}", 500

@application.route('/api/init-db', methods=['GET'])
def init_database():
    try:
        # Create all tables if they don't exist
        with application.app_context():
            db.create_all()
        return application.jsonify({"status": "Database initialized successfully"}), 200
    except Exception as e:
        logger.error(f"Database Initialization Error: {e}")
        logger.error(traceback.format_exc())
        return application.jsonify({"error": str(e)}), 500

def app(environ, start_response):
    """WSGI application with comprehensive error handling"""
    try:
        logger.info("WSGI application called")
        return application(environ, start_response)
    except Exception as e:
        logger.error("CRITICAL: WSGI Application Error")
        logger.error(f"WSGI Error Details: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Detailed error response
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        error_message = f"Application Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        return [error_message.encode('utf-8')]

# Expose the application for Vercel
__all__ = ['app', 'handler']

# Final startup log
logger.info("API module fully initialized and ready")
