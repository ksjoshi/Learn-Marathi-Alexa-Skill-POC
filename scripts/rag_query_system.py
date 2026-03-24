import os
import sys

# Add project root to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import generate_embedding
from app.services.translation_service import detect_language, translate_to_marathi
from app.services.search_service import search_documents
from app.services.rag_service import generate_answer_with_ollama

def query_knowledge_base(user_query):
    """Main function to query the knowledge base"""
    print(f"\nQuery: {user_query}")

    # Detect language
    query_language = detect_language(user_query)
    print(f"Detected language: {query_language}")

    # If English, translate to Marathi for better matching
    search_query = user_query
    if query_language == 'english':
        print("Translating query to Marathi for better search...")
        search_query = translate_to_marathi(user_query)
        print(f"Marathi query: {search_query}")

    # Search for similar documents
    print("\nSearching knowledge base...")
    query_embedding = generate_embedding(search_query)
    results = search_documents(query_embedding)

    if not results:
        return "Sorry, I couldn't find any relevant information."

    print(f"Found {len(results)} relevant chunks")
    
    # Build context
    context_parts = []
    for i, (content, english, metadata, similarity) in enumerate(results, 1):
        print(f"  {i}. Similarity: {similarity:.3f}")
        if similarity > 0.05:
            context_parts.append(f"Document {i}:\n{content}")
            if english:
                context_parts.append(f"(English: {english})")

    if not context_parts:
        return "Sorry, no information found with sufficient similarity."

    context = "\n\n".join(context_parts)

    # Generate response
    print("\nGenerating response...")
    response = generate_answer_with_ollama(context, user_query, response_language='marathi')

    return response

if __name__ == "__main__":
    while True:
        try:
            query = input("\nEnter your question (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break
            if not query.strip():
                continue

            answer = query_knowledge_base(query)
            print(f"\nAnswer: {answer}")
            print("-" * 80)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
