
class Model:
    def __init__(self):
        self.config = {
            "splitted_table_recognition": "heuristic",
            "ocr": "easyocr",
            "lang": "en",
            "threshold": 0.85
        }

    def get_config(self):
        return self.config


class ModelBuilder:
    def __init__(self):
        self.model = Model()

    def set_splitted_table_recognition(self, recognition_method: str):
        if recognition_method != "heuristic" and recognition_method != "model":
            raise ValueError("only allowed heuristic or model")
        self.model.config["splitted_table_recognition"] = recognition_method
        return self

    def set_ocr(self, ocr: str):
        if ocr != "tesseract" and ocr != "easyocr":
            raise ValueError("only allowed tesseract or easyocr")
        self.model.config["ocr"] = ocr
        return self

    def set_lang(self, lang: str):
        if lang not in ["pl", "en", "uk", "ru"]:
            raise ValueError("only allowed en, uk, pl, ru")
        self.model.config["lang"] = lang
        return self

    def set_threshold(self, threshold: float):
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("only allowed threshold in range (0.0, 1.0)")
        self.model.config["threshold"] = threshold
        return self

    def get_model(self):
        return self.model


class ModelDirector:

    @staticmethod
    def construct(method: str, ocr: str, lang: str, threshold: float):

        return ModelBuilder().set_splitted_table_recognition(method)\
                             .set_ocr(ocr)\
                             .set_lang(lang)\
                             .set_threshold(threshold)\
                             .get_model()


if __name__ == "__main__":
    model = ModelDirector.construct("model", "easyocr", "pl", 0.9)
    print(model.get_config())
    model = ModelDirector.construct("heuristic", "tesseract", "uk", 0.7)
    print(model.get_config())
