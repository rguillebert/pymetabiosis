from setuptools import setup, find_packages

setup(
    name="pymetabiosis",
    version="0.0.1",

    author="Romain Guillebert",
    author_email="romain.py@gmail.com",

    packages=find_packages(),
    license="MIT",
    description="A way of using CPython 2's modules on other cffi compatible Python implementations",

    install_requires=["cffi"],
)
