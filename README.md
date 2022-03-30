# WholeSlideData

[![PyPI version](https://badge.fury.io/py/wholeslidedata.svg)](https://badge.fury.io/py/wholeslidedata)

This repository contains software at a major version zero. Anything MAY change at any time. The public API SHOULD NOT be considered stable.

Please checkout the [CHANGELOG](https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/main/CHANGELOG.md) for updates for each version

-----
### Installation
pip install git+https://github.com/DIAGNijmegen/pathology-whole-slide-data@main

Wholeslidedata supports three image backends: openslide, ASAP, and pyvips. You will have to install additional software for these backends. You will only need one.

- For openslide please see installation instructions [here](https://openslide.org/download/)
- For ASAP please see installation  instructions [here](https://github.com/computationalpathologygroup/ASAP/releases/tag/ASAP-2.0-(Nightly))
- For pyvips please see installation instructions [here](https://anaconda.org/conda-forge/pyvips)

Openslide is currently the default image backend, but you can easily switch between different image backends in the config file. The options are 'openslide', 'asap' and 'pyvips'

For example:
```yaml
wholeslidedata:
    default:
        image_backend: asap
```




### Main Features

 - Image opening and patch extraction (ASAP, openslide-python and pyvips support)
 - Annotation opening and extraction (ASAP, QuPath, Virtum and Histomicstk support)
 - Batch iterator: iterator to be used for training a CNN
   - custom sampling strategies (various build-in strategies, e.g., random, balanced, area-based, and more)
   - custom sample/batch callbacks (various build in callbacks, e.g., fit_shape, one-hot-encoding, albumentations, and more)
   - multi-core patch extraction


### Examples:
Please see [notebook examples](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/notebooks) on how to use this code:


### Video Tutorials
Please see [video tutorials](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/tutorials) 

