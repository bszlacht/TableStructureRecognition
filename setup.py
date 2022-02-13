from setuptools import setup, find_packages


setup(
    name='server',
    packages=find_packages(),
    version='0.0.1',
    install_requires=[
        'numpy',
        'fastapi==0.71.0',
        'uvicorn==0.17.0',
        'pillow',
        'opencv-python',
        'scikit-learn',
        'pandas',
        'pytesseract',
        'easyocr',
        'srsly'
    ],
    package_data={'': ['*']}  # TODO maybe change to this
)
