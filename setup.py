from setuptools import setup, find_packages

setup(
    name="wholeslidedata",
    version="0.0.11",
    author="Mart van Rijthoven",
    author_email="mart.vanrijthoven@gmail.com",
    package_data={"": ["*.yml"]},
    packages=find_packages(exclude=("tests", "notebooks", "docs")),
    url="http://pypi.python.org/pypi/wholeslidedata/",
    license="LICENSE.txt",
    install_requires=[package.strip() for package in open("./requirements.txt").readlines()],
    long_description="Package for working with whole slide images.",
)
