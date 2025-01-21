import sys
import os
import traceback

# Detailed system path and import logging
print(f"Python Path: {sys.path}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"File Directory: {os.path.dirname(os.path.abspath(__file__))}")

# Attempt to import Flask and other dependencies
try:
    import flask
    import sqlalchemy
    print(f"Flask Version: {flask.__version__}")
    print(f"SQLAlchemy Version: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"Import Error: {e}")
    print(traceback.format_exc())
    raise

# Attempt to import application
try:
    from app import app as application, db
    print("Application imported successfully")
except Exception as e:
    print(f"Application Import Error: {e}")
    print(traceback.format_exc())
    raise

def handler(event, context):
    """Minimal Vercel handler for testing"""
    try:
        print("Vercel handler called")
        return {
            'statusCode': 200,
            'body': 'Test handler successful'
        }
    except Exception as e:
        print(f"Handler Error: {e}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': f'Handler Error: {str(e)}'
        }

def app(environ, start_response):
    """Minimal WSGI application for testing"""
    try:
        print("WSGI application called")
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'Vercel Deployment Test']
    except Exception as e:
        print(f"WSGI Error: {e}")
        print(traceback.format_exc())
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'WSGI Application Error']

# Expose for Vercel
__all__ = ['app', 'handler']

# Final startup log
print("API module fully initialized and ready")
