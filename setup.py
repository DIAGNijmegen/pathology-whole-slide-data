from setuptools import setup

setup(
    name="wholeslidedata",
    version="0.0.1",
    author="Mart van Rijthoven",
    author_email="mart.vanrijthoven@gmail.com",
    packages=["wholeslidedata"],
    url="http://pypi.python.org/pypi/wholeslidedata/",
    license="LICENSE.txt",
    install_requires=[
        "concurrentbuffer>=0.0.3",
        "creationism>=0.0.2",
        "numpy>=1.18.1",
        "opencv-python>=4.4.0",
        "scipy>=1.5.2",
        "scikit-image>=0.17.2",
        "shapely>=1.7.1",
        "openslide>=1.1.1",
        "PyYAML>=5.4.1"
    ],
    long_description="Package for working with whole slide images.",
)
