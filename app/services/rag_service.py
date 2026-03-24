import requests
from app.core.config import settings

def generate_answer_with_ollama(context: str, question: str, response_language: str = 'marathi') -> str:
    """Generate answer using Ollama with context"""

    # Determine response language instruction
    if response_language == 'marathi':
        language_instruction = "Answer in MARATHI (मराठी). Provide your response in Marathi language only."
    else:
        language_instruction = "Answer in the SAME LANGUAGE as the question."

    # Prompt matching the optimized one in the original script
    prompt = f"""You are a helpful assistant. You have access to information from documents.

IMPORTANT INSTRUCTIONS:
- Use ONLY the information provided in the context below
- If the context contains relevant information, provide a clear answer
- {language_instruction}
- Be specific and direct in your answer
- If you cannot find the answer in the context, say so clearly in Marathi

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {question}

ANSWER (in Marathi):"""

    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json={
                "model": settings.OLLAMA_GENERATE_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 150,
                }
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()

            if not answer:
                return "माहिती सापडली पण योग्य उत्तर तयार करता आले नाही. कृपया प्रश्न पुन्हा विचारा."

            return answer
        else:
            return "ओल्लामा पासून उत्तर मिळवताना त्रुटी आली."
    except requests.exceptions.Timeout:
        return "उत्तर देण्यास खूप वेळ लागत आहे. कृपया लहान प्रश्न विचारा."
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return f"त्रुटी: {str(e)}"
