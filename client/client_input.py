from api.service import Service
from input.file_reader import FileReader
from input.model_builder import ModelDirector

if __name__ == "__main__":
    file_reader = FileReader("demo.png")
    data_instance = file_reader.convert()
    model = ModelDirector.construct("model", "tesseract", "pl", 0.85)
    address = "127.0.0.1:80"
    service = Service(address)
    service.predict(model, data_instance)