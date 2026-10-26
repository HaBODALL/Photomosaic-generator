from setuptools import setup, find_packages

setup(
    name="photomosaic-generator",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless",
        "numpy",
        "scipy",
        "scikit-image",
        "requests",
        "python-dotenv",
        "streamlit",
        "Pillow",
    ],
    entry_points={
        "console_scripts": [
            "photomosaic=photomosaic.cli:main",
        ],
    },
)
