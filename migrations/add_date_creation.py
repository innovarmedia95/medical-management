from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabinet_medical.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

def add_date_creation_column():
    with app.app_context():
        # Add the column if it doesn't exist
        try:
            db.session.execute('ALTER TABLE patient ADD COLUMN date_creation DATETIME DEFAULT CURRENT_TIMESTAMP')
            db.session.commit()
            print("Column added successfully!")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == '__main__':
    add_date_creation_column()
