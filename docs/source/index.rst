:html_theme.sidebar_secondary.remove:


WholeSlideData
==============



.. grid:: 1

    .. grid-item::
        :class: sd-text-white sd-bg-primary sd-pt-3


        The wholeslidedata package aims to provide the tools to work with whole-slide images and annotations from different vendors and annotation software. The main contribution is a batch iterator that enables users to sample patches from the data efficiently, fast, and easily. 


.. grid:: 1

    .. grid-item::

        **Efficient**

        WholeSlideData preserves the annotations in a JSON format internally and uses the `Shapely <https://github.com/shapely/shapely>`_ library to do essential computations on basic geometries. Using this design ensures that the required memory to keep all the annotations in memory is more efficient than converting the annotations to masks. Furthermore, this package allows for the generation of patches and labels on the fly, which eludes the need for saving them to disk.

        **Fast**

        Extracting patches for whole-slide images is slow compared to saving the patches to PNGs or NumPy arrays and loading them directly from the disk. However, saving to disk is disadvantageous as this will generate a static dataset. For example, you can not switch easily to other patch shapes or magnifications with a static dataset. WholeSlideData takes advantage of `Concurrent Buffer <https://github.com/martvanrijthoven/concurrent-buffer>`_, which uses shared memory and allows for loading patches quickly via multiple workers to overcome the relatively slow serial extraction of patches from whole-slide images. However, using many extra CPUs will increase the RAM needed. Nevertheless, we think that with this package, a good trade-off can be made such that sampling is fast, efficient, and allows for easy switching to different settings.

        **Ease**

        WholeSlideData uses a configuration system called `Dicfg <https://github.com/martvanrijthoven/dicfg>`_ that allows users to configure the batch terator in a single config file. Using multiple configuration files is also possible to create a clean and well-structured configuration for your project. Dicfg has some parallels with Hydra. So if you are familiar with Hydra, it should be straightforward to make your configuration file for the batch iterator. Dicfg lets you configure any setting, build instances, and insert these instances as dependencies for other functions or classes directly in the config file. Furthermore, users can build on top of base classes and will only need to change the configuration file to use custom code without the need to change any part of the batch iterator.










.. toctree::
    :hidden:

    ./installation/index
    ./userguide/index
    ./userguide/examples
    ./api
    ./support