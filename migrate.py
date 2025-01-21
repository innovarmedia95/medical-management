from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate as migrate_command, upgrade

from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Initialize migrations
        init()
        
        # Create a migration
        migrate_command(message="Add date_creation column")
        
        # Apply migrations
        upgrade()
