
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
         label_map:
            stroma: 1
            tumor: 2
            lymphocytes: 3
         batch_shape:
            batch_size: 4
            spacing: 1.0
            shape: [512, 512, 3]


BatchIterator Components
***************************

Image backends
**************

To specify an image backend for the full dataset

This entails the images and image backend used to read from the images and the annotations and the parser that convert the annotations to the internal representations used in the batch iterator. The default image backend is 'openslide' and does not need to be configured. However, if you want to change the image backend, you can configure it as follows. 

.. button-link:: notebooks/components/dataconfig.html
    :color: primary
    :outline:
    :shadow:
    :align: right
    :class: sd-width-10, sd-height-10

    :octicon:`arrow-right;1em;` Image backends 




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

   ./notebooks/components/dataconfig
   ./notebooks/components/imagebackend
   ./notebooks/components/annotationparser
   ./notebooks/components/associations
   


.. toctree::
   :hidden:
   :caption: Data Settings

   ./notebooks/components/modes
   ./notebooks/components/labels
   ./notebooks/components/batchshape
   ./notebooks/components/dataset

.. toctree::
   :hidden:
   :caption: Samplers

   ./notebooks/components/labelsampler
   ./notebooks/components/annotationsampler
   ./notebooks/components/pointsampler
   ./notebooks/components/patchsampler
   ./notebooks/components/patchlabelsampler
   ./notebooks/components/samplesampler
   ./notebooks/components/batchsampler

.. toctree::
   :hidden:
   :caption: Customization

   ./notebooks/components/seed
   ./notebooks/components/presets
   ./notebooks/components/hooks

