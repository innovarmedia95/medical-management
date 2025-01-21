import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app import app as application
except Exception as e:
    print(f"Error importing application: {e}")
    raise

# This file is the entry point for Vercel
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Medical Management Application is running'
    }
