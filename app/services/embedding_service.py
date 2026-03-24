from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Global model instance
model = None

def get_model() -> SentenceTransformer:
    """Get the sentence transformer model, loading it if necessary"""
    global model
    if model is None:
        print(f"📦 Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
        model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        print("✅ Model loaded successfully!")
    return model

def generate_embedding(text: str):
    """Generate embedding for the given text"""
    embedding_model = get_model()
    return embedding_model.encode(text).tolist()
