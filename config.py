import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sampah-ai-prediction-system-secret-key-12345")
    
    # Database Configuration (MySQL as primary, fallback to SQLite if MySQL env is missing)
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "sistem_prediksi_sampah")
    
    # Primary MySQL URI
    MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # SQLite Fallback URI (useful for local development and testing)
    SQLITE_URI = "sqlite:///sistem_prediksi_sampah.db"
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", MYSQL_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # FastAPI Microservice URL
    FASTAPI_API_URL = os.environ.get("FASTAPI_API_URL", "http://localhost:8000")
