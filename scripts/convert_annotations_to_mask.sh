OUTPUT_FOLDER=/home/user/tiger_masks 
OUTPUT_SPACING=2.0

IMAGE_PATH=/data/pathology/projects/tiger/new_structure/training/wsirois/wsi-level-annotations/images/114S.tif
ANNOTATION_PATH=/data/pathology/projects/tiger/new_structure/training/wsirois/wsi-level-annotations/annotations-tissue-cells-xmls/114S.xml

python3 convert_annotations_to_mask.py \
    --image_path $IMAGE_PATH \
    --annotation_path $ANNOTATION_PATH \
    --output_folder $OUTPUT_FOLDER \
    --output_spacing $OUTPUT_SPACING \
    --label_mapping "invasive tumor"=1 \
    --label_mapping "tumor-associated stroma"=2 \
    --label_mapping "in-situ tumor"=3 \
    --label_mapping "healthy glands"=7 \
    --label_mapping "necrosis not in-situ"=5 \
    --label_mapping "inflamed stroma"=6 \
    --label_mapping "rest"=7 \
    -s area                                       
