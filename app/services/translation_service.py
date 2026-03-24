import requests
from app.core.config import settings

def detect_language(text: str) -> str:
    """Detect if text is Marathi or English"""
    devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    return 'marathi' if devanagari_chars > len(text) * 0.3 else 'english'

def translate_to_marathi(english_text: str) -> str:
    """Translate English query to Marathi using Ollama"""
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json={
                "model": settings.OLLAMA_TRANSLATE_MODEL,
                "prompt": f"""Translate this English question to simple Marathi. Use common words.

English: {english_text}

Marathi (simple and natural):""",
                "stream": False,
                "options": {
                    "temperature": 0.3
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            marathi_text = result.get('response', '').strip()
            # Clean up the translation
            marathi_text = marathi_text.split('\n')[0].strip()
            return marathi_text
        return english_text
    except Exception as e:
        print(f"Translation error: {e}")
        return english_text

def translate_to_english(marathi_text: str) -> str:
    """Translate Marathi text to English using Ollama (from pdf_to_vector.py)"""
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json={
                "model": settings.OLLAMA_TRANSLATE_MODEL,
                "prompt": f"Translate this Marathi text to English. Provide ONLY the English translation:\n\n{marathi_text}",
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        return None
    except Exception as e:
        print(f"Translation error: {e}")
        return None
