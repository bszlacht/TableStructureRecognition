from abc import abstractmethod, ABCMeta


class Model:
    def __init__(self):
        self.config = {
            "splitted_table_recognition": "",
            "ocr": ""
        }

    def get_config(self):
        return self.config


class IBuilder(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def set_splitted_table_recognition(self, recognition_method: str):
        pass

    @staticmethod
    @abstractmethod
    def set_ocr(self, ocr: str):
        pass


class ModelBuilder(IBuilder):
    def __init__(self):
        self.model = Model()

    def set_splitted_table_recognition(self, recognition_method: str):
        self.model.config["splitted_table_recognition"] = recognition_method
        return self

    def set_ocr(self, ocr: str):
        self.model.config["ocr"] = ocr
        return self

    def get_model(self):
        return self.model


class ModelDirector:

    @staticmethod
    def construct(method: str, ocr: str):

        return ModelBuilder().set_splitted_table_recognition(method)\
                             .set_ocr(ocr)\
                             .get_model()


if __name__ == "__main__":
    model = ModelDirector.construct("model", "easyocr")
    print(model.get_config())
    model = ModelDirector.construct("heuristic", "tesseract")
    print(model.get_config())
