from typing import List, Tuple, Any
from app.db.database import get_db_connection

def search_documents(query_embedding: List[float], top_k: int = 3) -> List[Tuple[Any, ...]]:
    """Search for similar documents in vector database"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT content, content_english, metadata,
                   1 - (embedding <=> %s::vector) as similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
                LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        )

        results = cur.fetchall()
        return results
    finally:
        cur.close()
        conn.close()
