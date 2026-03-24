from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.db.database import get_db_connection
from app.services.embedding_service import get_model

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_connected = False
    try:
        conn = get_db_connection()
        conn.close()
        db_connected = True
    except:
        pass

    model = None
    try:
        model = get_model()
    except:
        pass

    return HealthResponse(
        status="ok" if (model is not None and db_connected) else "degraded",
        model_loaded=model is not None,
        database_connected=db_connected
    )
