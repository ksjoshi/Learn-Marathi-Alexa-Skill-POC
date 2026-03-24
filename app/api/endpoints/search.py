from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse, SearchResult
from app.services.embedding_service import generate_embedding
from app.services.translation_service import detect_language, translate_to_marathi
from app.services.search_service import search_documents

router = APIRouter()

@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Semantic search endpoint

    Returns documents similar to the query based on vector similarity
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Detect language and translate if needed
        query_language = detect_language(request.query)
        search_query = request.query

        if query_language == 'english':
            search_query = translate_to_marathi(request.query)

        # Generate embedding for the (potentially translated) query
        query_embedding = generate_embedding(search_query)

        # Search database
        results = search_documents(query_embedding, request.top_k)

        # Format results
        formatted_results = [
            SearchResult(
                content=content,
                content_english=content_english,
                metadata=metadata,
                similarity=float(similarity)
            )
            for content, content_english, metadata, similarity in results
        ]

        return SearchResponse(
            success=True,
            count=len(formatted_results),
            results=formatted_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
