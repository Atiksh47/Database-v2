from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for React frontend if needed

# SQLAlchemy setup
DATABASE_URL = Config.get_database_url()
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL queries in console
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models (we'll create these next)
# from models import *

@app.route('/')
def hello():
    return {'message': 'Hello from CS348 Project API!'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
