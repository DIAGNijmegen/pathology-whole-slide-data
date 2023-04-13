:html_theme.sidebar_secondary.remove:

Installation
============

.. image:: https://badge.fury.io/py/wholeslidedata.svg
    :target: https://badge.fury.io/py/wholeslidedata  

.. image:: https://img.shields.io/badge/dockerhub-latest-blue.svg
   :target: https://hub.docker.com/repository/docker/martvanrijthoven/wholeslidedata
   :alt: Dockerhub version

.. image:: https://github.com/DIAGNijmegen/pathology-whole-slide-data/actions/workflows/docs.yml/badge.svg
    :target: https://github.com/DIAGNijmegen/pathology-whole-slide-data/actions/workflows/docs.yml

.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/DIAGNijmegen/pathology-whole-slide-data/HEAD


.. important::

   * wholeslidedata requires **python>=3.8**


.. code-block:: bash
   
   pip install git+https://github.com/DIAGNijmegen/pathology-whole-slide-data@main




Image Backend Installation
^^^^^^^^^^^^

The wholeslidedata packages requires an image backend to open whole-slide images.

.. attention::
   * Whole-slide data comes with **writing capabilties** for which **ASAP** is required.


Wholeslidedata supports three image backends based on `Openslide <https://openslide.org/api/python/>`_, `ASAP <https://computationalpathologygroup.github.io/ASAP/>`_, or `PyVips <https://libvips.github.io/pyvips/>`_. For these packages, additional software needs to be installed.

