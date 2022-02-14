from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi import Body
from starlette.responses import RedirectResponse
import srsly
from starlette.types import Message
import uvicorn

from models import (
    TableRecognitionRequest,
    TablesContentAndPositionResponse
)
from server.service.model_inference import ModelInference
from decoder import Decoder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-5s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(
    title='TableRecognition',
    version='1.0',
    description='Deployed table recognition model'
)

api_directory = Path(__file__).parent
example_request = srsly.read_json(api_directory / 'data' / 'example_request.json')

model = ModelInference()
decoder = Decoder()


@app.get('/', include_in_schema=False)
def docs_redirect():
    return RedirectResponse('/docs')


@app.post('/predict', response_model=TablesContentAndPositionResponse, tags=['table recognition'])
async def extract_entities(body: TableRecognitionRequest = Body(..., example=example_request)):
    """Recognize tables, their structures and content"""

    try:
        model_configuration = body.model.dict()

        tables = []
        for document in body.data:
            pages = [decoder.decode(page) for page in document.pages]
            for recognized_table in model.predict(pages, document.page_width, document.page_height,  model_configuration):
                recognized_table.update({'document_id': document.document_id})
                tables.append(recognized_table)
    except Exception as ex:
        logger.exception(ex)
        return {
            'tables': [],
            'errors': [{'message': str(ex)}]
        }

    logger.info('Sending response')

    return {"tables": tables}
