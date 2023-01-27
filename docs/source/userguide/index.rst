
User Guide
==========


Get Started
***********


* `Example Data <notebooks/components/downloaddata.html>`_
* `WholeSlideImage <notebooks/components/wholeslideimage.html>`_
* `WholeSlideAnnotation <notebooks/components/wholeslideannotation.html>`_
* `BatchIterator <notebooks/components/batchiterator.html>`_



Minimal BatchIterator Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   wholeslidedata:
      default:
         yaml_source:
            training:
            - wsi:
                 path: /tmp/TCGA-21-5784-01Z-00-DX1.tif
              wsa:
                 path: /tmp/TCGA-21-5784-01Z-00-DX1.xml
         labels:
            stroma: 1
            tumor: 2
            lymphocytes: 3
         batch_shape:
            batch_size: 4
            spacing: 1.0
            shape: [512, 512, 3]




.. toctree::
   :hidden:
   :caption: Get Started

   ./notebooks/components/downloaddata
   ./notebooks/components/wholeslideimage
   ./notebooks/components/wholeslideannotation
   ./notebooks/components/batchiterator

.. toctree::
   :hidden:
   :caption: Data Loading

   ./notebooks/components/data
   ./notebooks/components/imagebackend
   ./notebooks/components/annotationparser
   


.. toctree::
   :hidden:
   :caption: Data Settings

   ./notebooks/components/modes
   ./notebooks/components/labels
   ./notebooks/components/batchshape

.. toctree::
   :hidden:
   :caption: Samplers

   ./notebooks/components/labelsampler
   ./notebooks/components/annotationsampler
   ./notebooks/components/pointsampler
   ./notebooks/components/patchlabelsampler

.. toctree::
   :hidden:
   :caption: Customization

   ./notebooks/components/presets
   ./notebooks/components/callbacks

