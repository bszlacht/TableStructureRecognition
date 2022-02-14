from argparse import ArgumentParser
import json

from tsr import Service, FileReader, ModelDirector


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('filenames', nargs='+', help='filenames to process')
    parser.add_argument('output', help='filepath for the respond')
    parser.add_argument('--split_table', default='model', help='the way to process splitted tables (model|heuristic)')
    parser.add_argument('--library', default='easyocr', help='a library for the ocr (easyocr|tesseract)')
    parser.add_argument('--lang', default='en', help='language of the document (en|pl|ru|uk)')
    parser.add_argument('--threshold', type=float, default=0.85, help='threshold score for the output of the model')
    parser.add_argument('--address', default='127.0.0.1:8444', help='address of the server')

    args = parser.parse_args()

    file_reader = FileReader()
    data_instance = file_reader.read(*args.filenames)
    model = ModelDirector.construct(args.split_table, args.library, args.lang, args.threshold)
    service = Service(args.address)
    result = service.predict(model, data_instance)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
