from argparse import ArgumentParser
import json

from tsr import Service, FileReader, ModelDirector


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('output', help='filepath for the respond')
    args = parser.parse_args()

    file_reader = FileReader()
    data_instance = file_reader.read('demo.png')
    model = ModelDirector.construct("model", "easyocr", "en", 0.85)
    address = "127.0.0.1:8444"
    service = Service(address)
    result = service.predict(model, data_instance)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
