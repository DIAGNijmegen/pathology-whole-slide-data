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

-----
### Main Features

#### Image opening and patch extraction (ASAP, openslide-python and pyvips support)
```python
from wholeslidedata.image.wholeslideimage import WholeSlideImage
image = WholeSlideImage('path_to_image.tif') 
patch = image.get_patch(x, y, width, height, spacing)
```
#### Annotation opening and extraction (ASAP, QuPath, Virtum and Histomicstk support)
```python
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
wsa = WholeSlideAnnotation('path_to_annotation.xml')
annotations = wsa.select_annotations(x, y, width, height)
```

#### Batch iterator: iterator to be used for training a CNN
- custom sampling strategies (various build-in strategies, e.g., random, balanced, area-based, and more)
- custom sample/batch callbacks (various build in callbacks, e.g., fit_shape, one-hot-encoding, albumentations, and more)
- multi-core patch extraction
```python
from wholeslidedata.iterators import create_batch_iterator
training_iterator = create_batch_iterator(mode='training', 
                                          user_config='path_to_user_config.yml',
                                          number_of_batches=10,
                                          cpus=4) 
for x_batch, y_batch, info in training_iterator:
    pass
```

-----
### Examples & Video Tutorials:
Please see [notebook examples](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/notebooks) on how to use this code

Please also checkout the [video tutorials](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/tutorials) 
