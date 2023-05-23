from setuptools import setup, find_packages

setup(
    name="NeuralGPT",
    version="0.1",
    author="B staszewski",
    author_email="bstaszewski1984@gmail.com",
    description="A project for neural GPT",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "transformers",
        "pytest"
    ]
)