# Getting started

## Installation
```bash
pip install wholeslidedata
```

### WholeSlideImage
```python
from wholeslidedata.image.wholeslideimage import WholeSlideImage

with WholeSlideImage.open(path_to_wsi) as wsi:
    # print some properties
    print(f'available spacing in {wsi.path}:\n{wsi.spacings}\n')
    print(f'shapes in {wsi.path}:\n{wsi.shapes}\n')

    # extract a patch
    x, y = 20000,20000
    width, height = 512, 512
    spacing = 0.5 
    patch = wsi.get_patch(x, y, width, height, spacing)

## asap backend (default)
with WholeSlideImage.open(path_to_wsi, backend='asap') as wsi:
    print(f'Backend used: {wsi.__class__}\n')

## openslide backend
print("opening wsi with 'openslide' backend")
with WholeSlideImage.open(path_to_wsi, backend='openslide') as wsi:
    print(f'Backend used: {wsi.__class__}\n')


```


### WholeSlideAnnotation
```python
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation

# opening annotation file
wsa = WholeSlideAnnotation(annotation_path, labels=['tumor', 'stroma', 'til'])

# print some properties
print(f'\ncounts per label:  {wsa.counts_per_label}')
print(f'\npixels per label:  {wsa.pixels_per_label}')

# retrieving annotations
print(wsa.annotations)

```



### WholeSlideDataSet

path_to_data.yml:

    training:
        image_path: path_to_image
        annotation_path: path_to_annotation
        ...

    validation:
        image_path: path_to_image
        annotation_path: path_to_annotation
        ...


```python

from wholeslidedata import dataset

datasets = dataset.open_datasets_from_yaml(yaml_source='path_to_data.yml', 
                                           modes=('training', 'validation'), 
                                           labels=['tumor', 'stroma', 'til'])

# print training annotations per label per image
print(datasets['training'].annotations_per_label_per_image)

```