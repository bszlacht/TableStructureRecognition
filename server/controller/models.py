from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ModelConfigurationRequest(BaseModel):
    splitted_table_recognition: str = Field('heuristic', regex=r'heuristic|model')
    ocr: str = Field('tesseract', regex=r'tesseract|easyocr')
    # TODO add more configurable hyperparameters


class DocumentRequest(BaseModel):
    document_id: int
    pages: List[str]


class TableRecognitionRequest(BaseModel):
    model: ModelConfigurationRequest
    data: List[DocumentRequest]
    

class Message(BaseModel):
    message: str


class CoordinateResponse(BaseModel):
    x: int
    y: int


class BoundingBoxResponse(BaseModel):
    top_left: CoordinateResponse
    bottom_right: CoordinateResponse


class TableContentAndPositionResponse(BaseModel):
    document_id: int
    content: List[List[str]]
    page: Union[int, List[int]]
    bbox: Union[BoundingBoxResponse, List[BoundingBoxResponse]]
    cell_bboxs: List[List[BoundingBoxResponse]]


class TablesContentAndPositionResponse(BaseModel):
    tables: List[TableContentAndPositionResponse]
    errors: Optional[List[Message]]
    warnings: Optional[List[Message]]
