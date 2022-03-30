# WholeSlideData

[![PyPI version](https://badge.fury.io/py/wholeslidedata.svg)](https://badge.fury.io/py/wholeslidedata)

-----
#### This repository contains software at a major version zero. Anything MAY change at any time. The public API SHOULD NOT be considered stable. 
-----

### Installation
pip install git+https://github.com/DIAGNijmegen/pathology-whole-slide-data@main


### Main Features

 - Image opening and patch extraction (ASAP, openslide-python and pyvips support)
 - Annotation opening and extraction (ASAP, QuPath, Virtum and Histomicstk support)
 - Batch iterator: iterator to be used for training a CNN
   - custom sampling strategies (various build-in strategies, e.g., balanced, area-based and more)
   - custom sample/batch callbacks (various build in callbacks, e.g., fit_shape, one-hot-encoding and more)
   - multi-core patch extraction


### Examples:
Please see [notebook examples](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/notebooks) on how to use this code:


### Video Tutorials
Please see [video tutorials](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/tutorials) 

