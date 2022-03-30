from setuptools import setup, find_packages

version = {}
with open("wholeslidedata/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="wholeslidedata",
    version=version['__version__'],
    author="Mart van Rijthoven",
    author_email="mart.vanrijthoven@gmail.com",
    package_data={"": ["*.yml"]},
    packages=find_packages(exclude=("tests", "notebooks", "docs")),
    url="https://github.com/DIAGNijmegen/pathology-whole-slide-data",
    license="LICENSE.txt",
    install_requires=[package.strip() for package in open("./requirements.txt").readlines()],
    long_description="Package for working with whole slide images.",
)
