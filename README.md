----
# WholeSlideData

[![PyPI version](https://badge.fury.io/py/wholeslidedata.svg)](https://badge.fury.io/py/wholeslidedata)

This repository contains software at a major version zero. Anything MAY change at any time. The public API SHOULD NOT be considered stable.

Please checkout the [CHANGELOG](https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/main/CHANGELOG.md) for updates for each version and the API for the current PyPI deployed version can be found [here](https://diagnijmegen.github.io/pathology-whole-slide-data/).

- [Installation](#installation)
- [Main Features](#main-features)
- [Examples and Video Tutorials](#examples-and-video-tutorials)

-----
## Installation
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
## Main Features

### Image opening and patch extraction (ASAP, openslide-python and pyvips support)
```python
from wholeslidedata.image.wholeslideimage import WholeSlideImage
image = WholeSlideImage('path_to_image.tif') 
patch = image.get_patch(x, y, width, height, spacing)
```

### Annotation opening and extraction (ASAP, QuPath, Virtum and Histomicstk support)
```python
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
wsa = WholeSlideAnnotation('path_to_annotation.xml')
annotations = wsa.select_annotations(x, y, width, height)
```

### Batch iterator: iterator to be used for training a CNN

The batch generator needs to be configured via a *data* and *user config* file. In the user config file, custom and build-in sampling strategies can be configured, such as random, balanced, area-based, and more. Additionally. custom and build-in sample and batch callbacks can be composed such as fit_shape, one-hot-encoding, albumentations, and more. For a complete overview please check out the main [config file](https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/main/wholeslidedata/configuration/config_files/config.yml) and all the sub config files [here](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/wholeslidedata/configuration/config_files).

Here below we show a basic example of a data and user config file.

**Example of a basic data configuration file (data.yml):**
```yaml
training:
    - wsi: 
        path: /tmp/TCGA-21-5784-01Z-00-DX1.tif
      wsa: 
        path: /tmp/TCGA-21-5784-01Z-00-DX1.xml       


```

**Example of a basic user config file (user_config.yml):**
```yaml
wholeslidedata:
    default:
        yaml_source: data.yml
        
        label_map:
            stroma: 1
            tumor: 2
            lymphocytes: 3
            
        batch_shape:
            batch_size: 8
            spacing: 0.5
            shape: [256, 256, 3]
```           

**Creating a batch iterator**
```python
from wholeslidedata.iterators import create_batch_iterator
training_iterator = create_batch_iterator(mode='training', 
                                          user_config='user_config.yml',
                                          number_of_batches=10,
                                          cpus=4) 
for x_batch, y_batch, batch_info in training_iterator:
    pass
```

-----
## Examples and Video Tutorials
- Please see [notebook examples](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/notebooks) on how to use this code.
- Please also checkout the [video tutorials](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/tutorials).
