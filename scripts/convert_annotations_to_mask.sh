OUTPUT_FOLDER=/tmp/tiger_masks 
OUTPUT_SPACING=2.0

IMAGE_PATH=/data/datasets/tiger/tiger-training-data/wsirois/wsi-level-annotations/images/114S.tif
ANNOTATION_PATH=/data/datasets/tiger/tiger-training-data/wsirois/wsi-level-annotations/annotations-tissue-cells-xmls/114S.xml

python convert_annotations_to_mask.py \
    --image_path $IMAGE_PATH \
    --annotation_path $ANNOTATION_PATH \
    --output_folder $OUTPUT_FOLDER \
    --output_spacing $OUTPUT_SPACING \
    -l "invasive tumor"=1 \                         # label mapping, here you can remap the labels to any value
    -l "tumor-associated stroma"=2 \
    -l "in-situ tumor"=3 \
    -l "healthy glands"=4 \
    -l "necrosis not in-situ"=5 \
    -l "inflamed stroma"=6 \
    -l "rest"=7 \
    -s area                                         # how to sort labels (tiger annotations are desgined to work with area)
