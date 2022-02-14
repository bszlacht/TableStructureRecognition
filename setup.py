from setuptools import setup, find_packages


setup(
    name='tsr',
    packages=find_packages(include=['tsr', 'tsr.*']),
    # package_dir={'tsr': 'client'},
    version='0.0.1',
    install_requires=[
        'numpy',
        'pillow',
        'opencv-python',
        'PyMuPDF'
    ],
    package_data={'': ['*']}  # TODO maybe change to this
)
