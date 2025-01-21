import os
import sys
import traceback

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def log_error(error):
    """Log errors to a file or stderr"""
    error_log = os.path.join(os.path.dirname(__file__), 'error.log')
    with open(error_log, 'a') as f:
        f.write(f"Error: {error}\n")
        f.write(traceback.format_exc())
    print(f"Error logged: {error}", file=sys.stderr)

try:
    from app import app as application, db
except Exception as import_error:
    log_error(f"Import Error: {import_error}")
    raise

def create_tables():
    """Ensure database tables are created"""
    try:
        with application.app_context():
            db.create_all()
    except Exception as db_error:
        log_error(f"Database Creation Error: {db_error}")
        raise

# Initialize tables on import
create_tables()

def handler(event, context):
    """Vercel serverless function handler"""
    try:
        return {
            'statusCode': 200,
            'body': 'Medical Management Application is running'
        }
    except Exception as e:
        log_error(f"Handler Error: {e}")
        return {
            'statusCode': 500,
            'body': f'Application Error: {str(e)}'
        }

def app(environ, start_response):
    """WSGI application wrapper with error handling"""
    try:
        return application(environ, start_response)
    except Exception as e:
        log_error(f"WSGI Application Error: {e}")
        
        # Implement a basic error response
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'An error occurred while processing the request']

# Expose the application for Vercel
__all__ = ['app', 'handler']
