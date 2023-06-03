from setuptools import setup, find_packages

setup(
    name="pypisca",
    version="0.1",
    packages=find_packages(),
    author="r ramkumar",
    author_email="79623032+r3mkumar@users.noreply.github.com",
    description="A simple Python package to download and extract packages from PyPi",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/r3mkumar/pypisca",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)