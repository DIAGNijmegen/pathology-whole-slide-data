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
    install_requires=[
        "concurrentbuffer>=0.0.7",
        "creationism>=0.0.5",
        "numpy>=1.20.2",
        "opencv-python-headless>=4.4.0",
        "scipy>=1.5.2",
        "scikit-image>=0.17.2",
        "shapely>=1.7.1",
        "openslide-python>=1.1.1",
        "PyYAML>=5.4.1",
        "jsonschema>=4.4.0",
        "rtree==1.0.0",
    ],
    long_description="Package for working with whole slide images.",
)
