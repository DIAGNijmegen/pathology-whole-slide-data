----
# WholeSlideData

[![PyPI version](https://badge.fury.io/py/wholeslidedata.svg)](https://badge.fury.io/py/wholeslidedata)

This repository contains software at a major version zero. Anything MAY change at any time. The public API SHOULD NOT be considered stable.

Please checkout the [CHANGELOG](https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/main/CHANGELOG.md) and the [API](https://diagnijmegen.github.io/pathology-whole-slide-data/) for the currently deployed version in PyPI.

**Overview**

- [Introduction](#introduction)
- [Installation](#installation)
- [Main Features](#main-features)
- [Examples and Video Tutorials](#examples-and-video-tutorials)


----
## Introduction
WholeSlideData aims to provide the tools to work with whole slide images and annotations from different vendors and annotation software. The main contribution is a batch iterator that enables users to sample patches from the data efficiently, fast, and easily. 

> ### Efficient
> WholeSlideData preserves the annotations in a JSON format internally and uses the [Shapely](https://github.com/shapely/shapely) library to do essential computations on basic geometries. Using this design ensures that the required memory to keep all the annotations in memory is more efficient than converting the annotations to masks. Furthermore, this package allows for the generation of patches and labels on the fly, which eludes the need for saving them to disk.

> ### Fast
> Extracting patches for whole slide images is slow compared to saving the patches to PNGs or NumPy arrays and loading them directly from the disk. Though, saving to disk has some disadvantageous as this will generate a static dataset. For example, you can not switch easily to other patch shapes or magnifications with a static dataset. WholeSlideData takes advantage of [Concurrent Buffer](https://github.com/martvanrijthoven/concurrent-buffer), which uses shared memory and allows for loading patches quickly via multiple workers to overcome the relatively slow serial extraction of patches from whole slide images. Using many extra CPUs will increase the RAM needed. Nevertheless, we think that with this package, a good trade-off can be made such that sampling is fast, efficient, and allows for easy switching to different settings.

> ### Ease
> WholeSlideData uses a configuration system called [Creationism](https://github.com/martvanrijthoven/creationism) that allows users to configure the batch terator in a single config file. Using multiple configuration files is also possible to create a clean and well-structured configuration for your project. Creationism has some parallels with Hydra. So if you are familiar with Hydra, it should be straightforward to make your configuration file for the batch iterator. Creationism lets you configure any setting, build instances, and insert these instances as dependencies for other functions or classes directly in the config file. Furthermore, users can build on top of base classes and will only need to change the configuration file to use custom code without the need to change any part of the batch iterator.

-----
## Installation
```bash
pip install git+https://github.com/DIAGNijmegen/pathology-whole-slide-data@main
```

Wholeslidedata supports three image backends: openslide, ASAP, and pyvips. You will have to install additional software for these backends. You will only need one.

- Installation instructions for [Openslide](https://openslide.org/download/)
- Installation instructions for [ASAP](https://github.com/computationalpathologygroup/ASAP/releases/tag/ASAP-2.0-(Nightly))
- Installation instructions for [PyVips](https://anaconda.org/conda-forge/pyvips)

Openslide is currently the default image backend, but you can easily switch between different image backends in the config file. The options are 'openslide', 'asap' and 'pyvips'

For example:
```yaml
wholeslidedata:
    default:
        image_backend: asap
```

-----
## Main Features

### Whole-slide images 
Currently, wholeslidedata support image backends for openslide, ASAP, and pyvips.

```python
from wholeslidedata.image.wholeslideimage import WholeSlideImage

wsi = WholeSlideImage('path_to_image.tif') 
patch = wsi.get_patch(x, y, width, height, spacing)
```

### Whole-slide annotations
Current, wholeslidedata supports annotations from the following annotation software: ASAP, QuPath, Virtum, and Histomicstk.

```python
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation

wsa = WholeSlideAnnotation('path_to_annotation.xml')
annotations = wsa.select_annotations(x, y, width, height)
```

### Batch iterator
The batch generator needs to be configured via *user config* file. In the user config file, custom and build-in sampling strategies can be configured, such as random, balanced, area-based, and more. Additionally. custom and build-in sample and batch callbacks can be composed such as fit_shape, one-hot-encoding, albumentations, and more. For a complete overview please check out the main [config file](https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/main/wholeslidedata/configuration/config_files/config.yml) and all the [sub config files](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/wholeslidedata/configuration/config_files).

**Example of a basic user config file (user_config.yml)**
```yaml
--- 
wholeslidedata: 
  default: 
  
    yaml_source: 
      training: 
        - 
          wsa: 
            path: /tmp/TCGA-21-5784-01Z-00-DX1.xml
          wsi: 
            path: /tmp/TCGA-21-5784-01Z-00-DX1.tif
            
    label_map: 
      stroma: 1
      tumor: 2
      lymphocytes: 3
      
    batch_shape: 
      shape: [256, 256, 3]
      batch_size: 8
      spacing: 0.5
```           

**Creating a batch iterator**
```python
from wholeslidedata.iterators import create_batch_iterator

with create_batch_iterator(mode='training', 
                           user_config='user_config.yml',
                           number_of_batches=10,
                           cpus=4) as training_iterator:
                           
    for x_batch, y_batch, batch_info in training_iterator:
        pass
```

-----
## Examples and Video Tutorials
- [Notebook examples](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/notebooks)
- [Video tutorials](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/main/tutorials)


### Acknowledgements

Created in the [#EXAMODE](https://www.examode.eu/) project
