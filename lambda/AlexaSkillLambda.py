import json
import requests

def lambda_handler(event, context):
    """
    Alexa Skill handler with Ollama translation
    """

    # Log the incoming request
    print("Event:", json.dumps(event))

    # Get request type
    request_type = event['request']['type']
    print("Request type:", request_type)

    # Handle LaunchRequest (when user opens the skill)
    if request_type == 'LaunchRequest':
        return build_response("Hello! I can translate English to Marathi or answer questions about school. Just say translate or ask a question.")

    # Handle IntentRequest (when user says something)
    elif request_type == 'IntentRequest':
        intent_name = event['request']['intent']['name']
        print("Intent:", intent_name)

        if intent_name == 'TranslateIntent':
            # Get the text user wants to translate
            slots = event['request']['intent'].get('slots', {})
            english_text = slots.get('phrase', {}).get('value', '')

            if english_text:
                print(f"Translating: {english_text}")
                # Translate using Ollama
                marathi_text = translate_to_marathi(english_text)
                response_text = f"The Marathi translation is: {marathi_text}"
            else:
                response_text = "I didn't catch what you want me to translate. Please try again."

            return build_response(response_text)

        elif intent_name == 'MyIntent':
            return build_response("Hello, I am your friend! This is working great!")

        elif intent_name == 'SchoolIntent':
            # Get the query user wants to ask RAG system
            slots = event['request']['intent'].get('slots', {})
            query = slots.get('query', {}).get('value', '') or slots.get('question', {}).get('value', '')
            if query:
                print(f"Asking School RAG: {query}")
                # Get answer from RAG API
                answer = ask_school_question(query)
                response_text = answer
                print(f"RAG response: {response_text}")
            else:
                response_text = "What would you like to know about school? Please try again."

            return build_response(response_text)

        elif intent_name == 'AMAZON.HelpIntent':
            return build_response("You can ask me to translate English sentences to Marathi. Just say, translate, followed by your sentence. You can also ask about school.")

        elif intent_name == 'AMAZON.CancelIntent' or intent_name == 'AMAZON.StopIntent':
            return build_response("Goodbye!", end_session=True)

    # Handle SessionEndedRequest
    elif request_type == 'SessionEndedRequest':
        return build_response("", end_session=True)

    # Default response
    return build_response("I didn't understand that. Please try again.")


def ask_school_question(query):
    """
    Call the RAG API for school-related questions
    """
    # If Running from the AWS console, replace the below url with the exposed url.
    # I had used `ngrok` to expose the url.
    RAG_URL = "http://localhost:9999/rag/ask"

    try:
        print(f"Calling School RAG API at: {RAG_URL} with query: {query}")
        response = requests.post(
            RAG_URL,
            json={
                "query": query,
                "top_k": 3
            },
            timeout=7
        )

        print(f"RAG response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                answer = result.get('answer', '').strip()
                print(f"RAG answer: {answer}")
                return answer
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"RAG API internal error: {error_msg}")
                return "I couldn't find an answer to that school question."
        else:
            print(f"RAG API HTTP error: {response.status_code} - {response.text}")
            return "School information service is not available right now."

    except requests.exceptions.Timeout:
        print("RAG API request timed out")
        return "The request is taking too long. Please try a shorter question."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error to RAG: {str(e)}")
        return "Cannot connect to school information service. Please make sure it's running."
    except Exception as e:
        print(f"RAG API error: {str(e)}")
        return "Sorry, I couldn't get school information right now."


def translate_to_marathi(english_text):
    """
    Translate English text to Marathi using the Vector Search API
    """
    # If Running from the AWS console, replace the below url with the exposed url.
    # I had used `ngrok` to expose the url.
    TRANSLATE_URL = "http://localhost:9999/translate"

    # Limit text length to avoid timeouts
    if len(english_text) > 200:
        return "Sorry, that's too long. Please try a shorter sentence."

    try:
        print(f"Calling Translate API at: {TRANSLATE_URL}")

        response = requests.post(
            TRANSLATE_URL,
            json={
                "phrase": english_text
            },
            timeout=30
        )

        print(f"Translate API response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                marathi_text = result.get('translated_text', '').strip()
                print(f"Translation result: {marathi_text}")
                return marathi_text
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"Translate API internal error: {error_msg}")
                return "I couldn't translate that right now."
        else:
            print(f"Translate API HTTP error: {response.status_code} - {response.text}")
            return "Translation service is not available right now."

    except requests.exceptions.Timeout:
        print("Translate API request timed out")
        return "The translation is taking too long. Please try a shorter sentence."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error to Translate API: {str(e)}")
        return "Cannot connect to translation service. Please make sure it's running."
    except Exception as e:
        print(f"Translate API error: {str(e)}")
        return "Sorry, I couldn't translate that right now."


def build_response(speech_text, end_session=False):
    """
    Build the response JSON for Alexa
    """
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_text
            },
            'shouldEndSession': end_session
        }
    }