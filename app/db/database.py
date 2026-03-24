import psycopg2
from fastapi import HTTPException
from app.core.config import settings

def get_db_connection():
    """Get database connection"""
    try:
        return psycopg2.connect(**settings.DB_CONFIG)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
