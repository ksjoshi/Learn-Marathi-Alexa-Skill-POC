import fitz  # PyMuPDF
import json
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import os
import sys

# Add project root to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.database import get_db_connection
from app.services.embedding_service import generate_embedding
from app.services.translation_service import translate_to_english

# Set custom tessdata path if needed
custom_tessdata = os.path.expanduser('~/tessdata')
if os.path.exists(custom_tessdata):
    os.environ['TESSDATA_PREFIX'] = custom_tessdata
    print(f"Using custom tessdata path: {custom_tessdata}")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using OCR for scanned PDFs"""
    doc = fitz.open(pdf_path)
    text_chunks = []

    print(f"PDF has {len(doc)} pages")

    for page_num in range(len(doc)):
        page = doc[page_num]

        # First try normal text extraction
        text = page.get_text("text")

        # If no text found, it's a scanned PDF - use OCR
        if not text.strip():
            print(f"Page {page_num + 1}: Scanned page detected, using OCR...")

            # Convert page to image with high resolution
            mat = fitz.Matrix(4, 4)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Preprocess image
            img = img.convert('L')
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.5)
            img = img.filter(ImageFilter.SHARPEN)

            # Perform OCR
            try:
                text = pytesseract.image_to_string(img, lang='mar', config='--psm 6')
                print(f"  OCR extracted {len(text)} characters")
            except Exception as e:
                print(f"  OCR error: {e}")
                text = ""
        else:
            print(f"Page {page_num + 1}: Extracted {len(text)} characters (native text)")

        # Process extracted text into chunks
        if text.strip():
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            current_chunk = []
            chunk_count = 0

            for i, line in enumerate(lines):
                current_chunk.append(line)
                is_new_topic = any(line.startswith(str(n) + '.') for n in range(1, 20))

                if len(current_chunk) >= 3 or (is_new_topic and len(current_chunk) >= 2):
                    chunk_text = ' '.join(current_chunk).strip()
                    if len(chunk_text) > 15:
                        chunk_count += 1
                        text_chunks.append({
                            'content': chunk_text,
                            'page': page_num + 1
                        })
                    current_chunk = []

            if current_chunk:
                chunk_text = ' '.join(current_chunk).strip()
                if len(chunk_text) > 15:
                    text_chunks.append({
                        'content': chunk_text,
                        'page': page_num + 1
                    })

    doc.close()
    return text_chunks

def store_in_database(chunks):
    """Store text chunks and embeddings in PostgreSQL"""
    conn = get_db_connection()
    cur = conn.cursor()

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        marathi_text = chunk['content']

        # Translate to English
        english_text = translate_to_english(marathi_text)

        # Generate embeddings
        embedding = generate_embedding(marathi_text)

        # Store in database
        metadata = json.dumps({'page': chunk['page']})

        cur.execute(
            """
            INSERT INTO documents (content, content_english, embedding, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (marathi_text, english_text, embedding, metadata)
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nSuccessfully stored {len(chunks)} chunks in database!")

def main():
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("Enter path to your Marathi PDF: ")

    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        return

    print("\n1. Extracting text from PDF...")
    chunks = extract_text_from_pdf(pdf_path)
    print(f"   Found {len(chunks)} text chunks")

    print("\n2. Processing and storing in database...")
    store_in_database(chunks)

if __name__ == "__main__":
    main()
