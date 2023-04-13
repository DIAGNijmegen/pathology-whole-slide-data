Support
=======

Welcome to our support page! If you encounter any problems, you can find answers to most common issues here. If you can't find the answer you're looking for or encounter a new issue, please open a GitHub issue and we'll respond as soon as possible.



Image backends
^^^^^^^^^^^^^^
To use the wholeslidedata package, you need to have at least one of the following image backends installed on your system:

* ASAP (https://github.com/computationalpathologygroup/ASAP/releases)
* OpenSlide (https://openslide.org/download/)
* PyVips (https://github.com/libvips/pyvips)

Please follow the links above for installation instructions for the specific image backend you'd like to use.


Openslide DLL error on windows
##############################

If you're encountering DLL-related errors while using the openslide module in Python, you can add the directory containing the required DLL file (libopenslide-0.dll) to the system's PATH using the os.add_dll_directory function. Here's an example:

.. code-block::

    import os

    os.add_dll_directory('C:/Program Files/OpenSlide/bin')


Batch iterator hanging
^^^^^^^^^^^^^^^^^^^^^^

The wholeslidedata package supports multiprocessing to speed up patch extraction and other processing tasks. On Unix systems, we recommend using "fork" instead of "spawn" when using notebooks to avoid issues with hanging processes.

On Windows systems, only "spawn" is available. Make sure you set the context argument to "spawn" when creating a batch iterator. However, using "spawn" may also cause issues with hanging processes, particularly in Jupyter notebooks. If you encounter an issue where your notebook appears to hang without giving an error message, try switching to a non-notebook environment.