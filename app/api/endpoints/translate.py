from fastapi import APIRouter, HTTPException
from app.models.schemas import TranslateRequest, TranslateResponse
from app.services.translation_service import translate_to_marathi

router = APIRouter()

@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translation endpoint to translate English text to Marathi
    """
    if not request.phrase.strip():
        raise HTTPException(status_code=400, detail="Phrase cannot be empty")

    try:
        translated_text = translate_to_marathi(request.phrase)

        return TranslateResponse(
            success=True,
            translated_text=translated_text
        )
    except Exception as e:
        print(f"ERROR in translate endpoint: {str(e)}")
        return TranslateResponse(
            success=False,
            translated_text="",
            error=str(e)
        )
