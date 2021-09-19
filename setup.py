from setuptools import setup, find_packages

setup(
    name="wholeslidedata",
    version="0.0.6",
    author="Mart van Rijthoven",
    author_email="mart.vanrijthoven@gmail.com",
    package_data={"": ["*.yml"]},
    packages=find_packages(exclude=("tests", "notebooks")),
    url="http://pypi.python.org/pypi/wholeslidedata/",
    license="LICENSE.txt",
    install_requires=[
        "concurrentbuffer>=0.0.3",
        "creationism>=0.0.3",
        "numpy>=1.18.1",
        "opencv-python>=4.4.0",
        "scipy>=1.5.2",
        "scikit-image>=0.17.2",
        "shapely>=1.7.1",
        "openslide-python>=1.1.1",
        "PyYAML>=5.4.1",
    ],
    long_description="Package for working with whole slide images.",
)
