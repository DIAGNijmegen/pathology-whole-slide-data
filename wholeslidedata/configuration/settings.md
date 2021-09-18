# WholeSlideData Configuration Settings

The end goal of the wholeslidedata configurtion is to create a WholeSlideDataSet. Th configuration does did via  which various components which are the building blocks required for a WholeSlideDataset. In this file the possible settings are discussed.

Please note that dictionaries can be placed, indented and under the setting or a seperate .yml file can be referenced which contains the dictionart definition. this seprate .yml should be within the same folder the custom config file or should be referenced with the full path

you have simple settings like int, strings, lists or dictionaries but you can also define object style preferences.
the format is as follows

```
setting:
    module: module.reference
    attribute: class
    arg1: name
    arg2: ${reference_to_other_setting}
    arg3: True
```
the module indicates the in which module the object or function is defined
The attribute is the class or function that you would like to create or call
The rest of the arguments are the arguments expected by the class or function. These arguments can also be linked to previous setting defined in the configuration file. We will see this in action when showing the annotation_backend setting. 



## yaml_source: 
This setting lets you define the data used for the dataset. There are various ways to structure the yaml file but the most straightforward and recommend way is like this:


```
yaml_source: path_to_data.yml
```

path_to_data.yml:
```
training: 
    - image_path: full_path_to_training_image_file{.tif, .tiff, .mrxs, .svs, ndpi}
      annotation_path: full_path_to_training_annotation_file{.xml, .json, .tif, .tiff}

    - image_path: full_path_to_training_image2_file{.tif, .tiff, .mrxs, .svs, ndpi}
      annotation_path: full_path_to_training_annotation2_file{.xml, .json, .tif, .tiff}

validation: 
    - image_path: full_path_to_validation_image_file{.tif, .tiff, .mrxs, .svs, ndpi}
      annotation_path: full_path_to_validation_annotation_file{.xml, .json, .tif, .tiff}

    - image_path: full_path_to_validation_image2_file{.tif, .tiff, .mrxs, .svs, ndpi}
      annotation_path: full_path_to_validation_annotation2_file{.xml, .json, .tif, .tiff}
    
```


## label_map: 
The label map lets you set the label_names and corresponding values that they should take on
The label names should correspond to the label names in the annotation files. e.g.,
```
label_map:
    label1: 1
    label2: 2
    label3: 1

```

## out_labels:
with out labels you can rename your labels. This is handy if you have multiple labels with the same value
```
out_labels:
    renamed_label: 1
    label2: 2
```

## image_backend:
currently there are two image backends (i.e., the software which images are opened) supported namely, asap and openslide, you can switch between via the image_bakcend setting. asap is the standard setting
```
image_backend: openslide
```

## annotation_backend:
Currently support annotation backends are asap, htk, qupath, virtum, you can switch between them in a similar way as the image backend. However if you would like to change particular settings you can also set them here e.g.,
```
annotation_backend: 
  module: wholeslidedata.annotation.parser
  attribute: AsapAnnotationParser
  labels: ${labels}
  out_labels: ${out_labels}
  scaling: 1.0
  sample_annotation_types: ["Polygon"]
```


## Custom configuration file

These settings can all be set for different modes: default, training, validation, testing, inference. An example of a custom config file could be:


```
wholeslidedata:
    default:
        yaml_source: path_to_data.yml

        label_map:
            label1: 1
            label2: 2
            label3: 3

```