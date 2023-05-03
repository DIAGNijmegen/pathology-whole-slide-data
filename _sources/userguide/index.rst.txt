
User Guide
==========


Get Started
***********


* `Example Data <notebooks/components/downloaddata.html>`_
* `WholeSlideImage <notebooks/components/wholeslideimage.html>`_
* `WholeSlideAnnotation <notebooks/components/wholeslideannotation.html>`_
* `BatchIterator <notebooks/components/batchiterator.html>`_


BatchIterator Overview
**********************

The BatchIterator is designed to extract patches from Whole Slide Images (WSIs) and their corresponding annotations, in order to generate labeled training data for machine learning models. The system works by defining a sampling strategy, which involves sampling labels, annotations, and points within the annotations. Based on this strategy, the system selects a patch to extract from the WSI and creates a corresponding label.

Data Preparation
^^^^^^^^^^^^^^^^

To prepare the data for sampling, the following steps are taken:

* **Associations**
      * WSIs and their corresponding annotation files (WSAs) are matched and stored as "associations".
      * Each association consists of a matched WSI file and WSA file.
      * Each WSI file has an image backend
      * Each WSA file has an annotation parser.

* **Parsing annotations:** All WSAs are parsed by their annotation parsers to extract a list of annotations (polygons, points).
* **Labels**: All available labels are gathered from all annotations.
* **Annotation mapping**: All annotations are mapped to their respective labels.


Sampling Strategy
^^^^^^^^^^^^^^^^^
The sampling strategy consists of three sampler components:

* **Step 1 - label_sampler**: samples a label from the available labels.
* **Step 2 - annotation_sampler**: samples an annotation from the list of annotations that corresponds to the label sampled in step 1.
* **Step 3 - point_sampler**: samples a point within the annotation sampled in step 2.


Sampling Data
^^^^^^^^^^^^^
The data sampling consists of two sampler components

* **Step 4 - patch_sampler**: selects a patch with a center point based on the point sampled in step 3 of the *sampling strategy*.
* **Step 5 - patch_label_sampler**: creates a label (classification, detection, or segmentation) based on the point sampled in step 3 of the *sampling strategy*.

By repeating the above steps, the BatchIterator generates patches and corresponding labels for use in machine learning models.


Minimal BatchIterator Configuration
***********************************

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

.. toctree::
   :hidden:
   :caption: Iterators

   ./notebooks/components/batchiterator
   ./notebooks/components/patchiterator

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

