from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi import Body
from starlette.responses import RedirectResponse
from starlette.types import Message
import uvicorn

from models import (
    OCRRequest,
    OCRResponse
)
from decoder import Decoder
from ocr import OCR


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(
    title='Optical Character Recognition',
    version='1.0',
    description='Deployed EasyOCR'
)

api_directory = Path(__file__).parent

ocr = None
decoder = Decoder()


@app.get('/', include_in_schema=False)
def docs_redirect():
    return RedirectResponse('/docs')


@app.post('/recognize', response_model=OCRResponse, tags=['optical character recognition'])
async def extract_entities(body: OCRRequest = Body(...)):
    try:
        ocr = OCR(body.library, body.lang)

        images = [decoder.decode(image) for image in body.images]
        texts = [ocr.recognize(image) for image in images]

        ocr = None
    except Exception as ex:
        logger.exception(ex)
        return {
            'texts': [],
            'errors': [{'message': str(ex)}]
        }

    return {
        'texts': texts
    }
