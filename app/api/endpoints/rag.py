from fastapi import APIRouter, HTTPException
from app.models.schemas import AskRequest, AskResponse
from app.services.embedding_service import generate_embedding
from app.services.translation_service import detect_language, translate_to_marathi
from app.services.search_service import search_documents
from app.services.rag_service import generate_answer_with_ollama

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    RAG-based question answering endpoint
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Detect language and translate if needed
        query_language = detect_language(request.query)
        search_query = request.query

        if query_language == 'english':
            search_query = translate_to_marathi(request.query)

        # Generate embedding and search
        query_embedding = generate_embedding(search_query)
        results = search_documents(query_embedding, request.top_k)

        if not results:
            return AskResponse(
                success=True,
                answer="तुमच्या प्रश्नाचे उत्तर देण्यासाठी संबंधित माहिती सापडली नाही.",
                context_used=0,
                top_similarity=None
            )

        # Build context
        context_parts = []
        for i, (content, english, metadata, similarity) in enumerate(results, 1):
            if similarity > 0.05:  # Consistent threshold
                context_parts.append(f"Document {i}:\n{content}")
                if english and len(english.strip()) > 0:
                    context_parts.append(f"(English: {english})")

        if not context_parts:
            return AskResponse(
                success=True,
                answer="पुरेशी संबंधित माहिती सापडली नाही.",
                context_used=0,
                top_similarity=float(results[0][3]) if results else None
            )

        context = "\n\n".join(context_parts)
        
        # Generate answer with Ollama
        answer = generate_answer_with_ollama(context, request.query, response_language='marathi')

        return AskResponse(
            success=True,
            answer=answer,
            context_used=len(context_parts),
            top_similarity=float(results[0][3]) if results else None
        )

    except Exception as e:
        print(f"ERROR in ask endpoint: {str(e)}")
        return AskResponse(
            success=False,
            answer="",
            context_used=0,
            top_similarity=None,
            error=str(e)
        )
