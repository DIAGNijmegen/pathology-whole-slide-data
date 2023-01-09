
User Guide
==========

texttexttexttexttexttexttexttexttexttexttext

texttexttexttexttexttexttexttexttexttextv
texttexttexttexttexttexttexttexttexttexttexttexttexttexttext

Get started
***********

Download example data



.. grid:: 1

   .. grid-item-card:: WholeSlideImage
      :link: notebooks/components/wholeslideimage.html
      :margin: 3 0 0 0
      

      texttexttexttexttexttextt
      texttexttexttexttexttextt
      texttexttexttexttexttextt


   .. grid-item-card:: WholeSlideAnnotation
      :link: notebooks/components/wholeslideannotation.html
      :margin: 3 0 0 0
      
      texttexttexttexttexttextt
      texttexttexttexttexttextt
      texttexttexttexttexttextt
      


   .. grid-item-card:: BatchIterator
      :link: notebooks/components/batchiterator.html
      :margin: 3 0 0 0
      
      texttexttexttexttexttextt
      texttexttexttexttexttextt
      texttexttexttexttexttextt
      


BatchIterator Configuration
***************************


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
   ./notebooks/components/hooks

