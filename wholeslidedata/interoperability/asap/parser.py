import xml.etree.ElementTree as ET

from wholeslidedata.annotation.parser import (
    AnnotationParser,
    AnnotationType,
    InvalidAnnotationParserError,
)
from wholeslidedata.annotation.labels import Labels
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend

class AsapAnnotationParser(AnnotationParser):

    TYPES = {
        "polygon": AnnotationType.POLYGON,
        "rectangle": AnnotationType.POLYGON,
        "dot": AnnotationType.POINT,
        "spline": AnnotationType.POLYGON,
        "pointset": AnnotationType.POINT,
    }

    @staticmethod
    def get_available_labels(opened_annotation):
        labels = []
        for parent in opened_annotation:
            for child in parent:
                if child.tag == "Annotation":
                    labels.append(child.attrib.get("PartOfGroup").lower().strip())
        return Labels.create(set(labels))
        

    def _open_annotation(self, path):

        tree = ET.parse(path)
        opened_annotation = tree.getroot()

        return opened_annotation


    def _parse(self, path):

        root = self._open_annotation(path)

        labels = self._get_labels(root)
        for parent in root:
            for child in parent:

                if child.tag != "Annotation":
                    continue

                type = self._get_annotation_type(child)

                label = self._get_label(root, child, labels, type)
                if label is None:
                    continue

                for coordinates in self._yield_coordinates(child, type):
                    yield {
                        "coordinates": coordinates,
                        "label": label,
                    }

    def _get_annotation_type(self, child):
        annotation_type = child.attrib.get("Type").lower()
        if annotation_type in AsapAnnotationParser.TYPES:
            return AsapAnnotationParser.TYPES[annotation_type]
        raise ValueError(f"unsupported annotation type in {child}")

    def _get_label(self, root, child, labels: Labels, type):
        name = self._get_label_name(child, labels, type)
        
        # try:
        #     color = root.find(f".//Group[@Name='{name}']").get("Color")
        # except AttributeError:
        #     color = None

        name = name.lower().strip()
        if name not in labels.names:
            return None

        label = labels.get_label_by_name(name)
        label = label.todict()
    
        # if 'color' not in label or label['color'] is None:
        #     if color is not None:
        #         label["color"] = color

        return label

    def _get_label_name(self, child, labels, type) -> str:
        if type in labels.names:
            return type
        return child.attrib.get("PartOfGroup")

    def _yield_coordinates(self, child, type):
        coordinates = []
        coordinate_structure = child[0]
        coordinates = self._get_coordinates(coordinate_structure)
        if type is AnnotationType.POLYGON:
            if len(coordinates) < 3:
                raise InvalidAnnotationParserError(f"Polygon contains < 3 coordinates")
            yield coordinates
        elif type is AnnotationType.POINT and len(coordinates) > 1:
            for coordinate in coordinates:
                yield coordinate
        else:
            yield coordinates[0]

    def _get_coordinates(self, coordinate_structure):
        return [
            [
                float(coordinate.get("X").replace(",", ".")),
                float(coordinate.get("Y").replace(",", ".")),
            ]
            for coordinate in coordinate_structure
        ]


class MaskAnnotationParser(AnnotationParser):
    def __init__(
        self,
        labels=("tissue",),
        processing_spacing=4.0,
        output_spacing=0.5,
        shape=(1024, 1024),
        backend=AsapWholeSlideImageBackend,
        full_coverage=False,
        offset=(0,0),
    ):
        super().__init__(labels=labels)
        self._processing_spacing = processing_spacing
        self._output_spacing = output_spacing
        self._shape = np.array(shape)
        self._backend = backend
        self._offset = offset
        self._np_check_tissue = np.all if full_coverage else np.any

    def get_available_labels(opened_annotation: Any) -> Labels:
        return Labels.create({"tissue": 1})

    def _parse(self, path):
        mask = WholeSlideImage(path, backend=self._backend)

        size = self._shape[0]
        ratio = self._processing_spacing / self._output_spacing

        y_offset = int(self._offset[1] // ratio)
        x_offset = int(self._offset[0] // ratio)

        np_mask = mask.get_slide(self._processing_spacing).squeeze()
        shape = np.array(np_mask.shape)

        new_shape = shape + size // ratio - shape % (size // ratio)
        new_mask = np.zeros(new_shape.astype("int"), dtype="uint8")
        new_mask[: shape[0]-y_offset, : shape[1]-x_offset] = np_mask[y_offset:, x_offset:]

        for annotation in self._get_annotations(new_mask, size, ratio):
            yield annotation

        mask.close()
        mask = None
        del mask

    def _get_annotations(self, new_mask, size, ratio):
        region_index = -1
        blocks = block(new_mask, int(size // ratio), int(size // ratio))
        for y in range(new_mask.shape[0] // (int(size // ratio))):
            for x in range(new_mask.shape[1] // int((size // ratio))):
                region_index += 1
                if not self._np_check_tissue(blocks[region_index]):
                    continue

                box = self._get_coordinates((x * size)+self._offset[0], (y * size)+self._offset[1], size, size)
                yield {
                    "coordinates": np.array(box),
                    "label": {"name": "tissue", "value": 1},
                }

    def _get_coordinates(self, x_pos, y_pos, x_shift, y_shift) -> List:
        box = geometry.box(x_pos, y_pos, x_pos + x_shift, y_pos + y_shift)
        return np.array(box.exterior.xy).T.tolist()

    def _check_mask(self, mask_patch):
        if np.any(mask_patch):
            return np.unique(mask_patch, return_counts=True)
        return None, None
