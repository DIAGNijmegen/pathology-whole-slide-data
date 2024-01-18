import argparse
from pathlib import Path
from shapely import geometry
from shapely.ops import unary_union
from wholeslidedata.interoperability.asap.annotationwriter import write_asap_annotation
from wholeslidedata.annotation.types import Annotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.annotation.labels import Label
from tqdm import tqdm
from scipy.ndimage import binary_erosion, binary_dilation
import numpy as np
import cv2
from wholeslidedata.annotation.utils import write_json_annotations
from typing import List, Optional
from ast import literal_eval

def polygon_value_and_index_to_outer_inner(value, index, hierarchies_dict):
    """cv2_polygonize_with_hierarchy helper function: checks if poligon is outer (exterior) or inner (a hole) based on the hierarchy of the polygon"""
    hierarchy = hierarchies_dict[value][index]
    return 'outer' if hierarchy[3]==-1 else 'inner'

def polygons_dict_to_outer_polygons_dict(polygons_dict, hierarchies_dict, inv_label_map=None):
    """cv2_polygonize_with_hierarchy helper function: converts a dict of polygons to a dict of outer polygons, based on the hierarchy of the polygons. We typically only want to keep the outer polygons because WSD cannot read holes"""
    polygons_outer_dict = {}
    for value, polygons in polygons_dict.items():
        polygons_outer = [polygon for polygon_idx, polygon in enumerate(polygons) \
                          if polygon_value_and_index_to_outer_inner(value, polygon_idx, hierarchies_dict) == 'outer']
        label_name = f'class value {value}'
        if inv_label_map:
            label_name=inv_label_map[value]
        print(f'\t\t{label_name}: \n\t\t\tfrom {len(polygons)} polygons, {len(polygons_outer)} were outer, {len(polygons) - len(polygons_outer)} holes were removed')
        polygons_outer_dict[value] = polygons_outer
    return polygons_outer_dict

def cv2_polygonize_with_hierarchy(
    mask, dilation_iterations=0, erose_iterations=0, exclude_holes=True, values=None, inv_label_map=None):
    """converts a mask to a dict of polygons, with the option to exclude holes, based on 2 step hierarchy (exteriors and holes)."""
    if values is None:
        values = np.unique(mask)

    all_polygons = {}
    all_hierarchies = {}

    print('\tExtracting polygons with exterior/hole hierachy')
    for value in values:
        print(f'\t\tprocessing value {value}{f", {inv_label_map[value]}" if inv_label_map else ""}')
        
        tmp_mask = (mask == value).astype(np.uint8) # improved here, allowing to extraxt background polygons (if you dont want background, exclude its value from 'values' input)

        if dilation_iterations > 0:
            tmp_mask = binary_dilation(tmp_mask, iterations=dilation_iterations).astype(
                np.uint8
            )
        if erose_iterations > 0:
            tmp_mask = binary_erosion(tmp_mask, iterations=erose_iterations).astype(
                np.uint8
            )

        tmp_mask = np.pad(
            array=tmp_mask, pad_width=1, mode="constant", constant_values=0
        )

        
        polygons, hierarchies = cv2.findContours(
            tmp_mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE, offset=(-1, -1) #cv2.RETR_CCOMP retuns hierarchy with outer/hole inforamtion
        )
        
        if len(polygons)==0:
            all_polygons[value] = []
            all_hierarchies[value] = []
            continue
        
        # remove instances with <3 coordinates
        filtered_polygonsand_hierarchies = [(np.array(polygon[:, 0, :]), hierarchy)
                for polygon, hierarchy in zip(polygons, hierarchies[0])
                if len(polygon) >= 3]
        if len(filtered_polygonsand_hierarchies) == 0:
            all_polygons[value] = []
            all_hierarchies[value] = []
            continue
        polygons, hierarchies = zip(*filtered_polygonsand_hierarchies)
        
        all_polygons[value] = polygons 
        all_hierarchies[value] = hierarchies
        
    
    if exclude_holes:
        print('\tRemoving hole polygons')
        all_polygons = polygons_dict_to_outer_polygons_dict(all_polygons, all_hierarchies, inv_label_map)
    
    return all_polygons

def convert_polygons_to_annotations(polygons, inv_label_map, color_map):
    """converts a dict of polygons to a list of annotations for file export"""
    annotation_structures = []
    index = 0
    for value, polys in polygons.items():
        for polygon in polys:
            p = geometry.Polygon(polygon).buffer(0)
            label = Label(
                name=inv_label_map[value],
                value=value,
                color=color_map[inv_label_map[value]]
            )
            if isinstance(p, geometry.MultiPolygon):
                for q in list(p):
                    annotation_structure = dict(
                        index=index,
                        # type="polygon",
                        label=label.todict(),
                        coordinates=q.exterior.coords,
                        # holes=[],
                    )
                    annotation_structures.append(annotation_structure)
                    index += 1
            else:
                annotation_structure = dict(
                    index=index,
                    # type="polygon",
                    label=label.todict(),
                    coordinates=p.exterior.coords,
                    # holes=[],
                )
                annotation_structures.append(annotation_structure)
                index += 1

    annotations = []
    for annotation_structure in annotation_structures:
        if len(annotation_structure["coordinates"]) >= 3:
            try:
                annotation = Annotation.create(**annotation_structure)
            except Exception as e:
                print(annotation_structure["coordinates"])
                raise e
            annotations.append(annotation)
    return annotations

def convert_annotations_to_json(annotations: List[Annotation], scaling: Optional[float] = None):
    output = []
    for annotation in annotations:
        item = annotation.todict()
        if scaling is not None:
            new_coordinates = [[coord[0] * scaling, coord[1] * scaling] for coord in item['coordinates']]
            item['coordinates'] = new_coordinates
        output.append(item)
    return output

def labels_to_label_and_color_mapping(labels):
    """labels should be a dict with label names as keys and label values as values"""
    label_mapping = {v:k for k,v in labels.items()}
    original_colormap = [ [0, 0, 0, 255], [ 0, 224, 249, 255 ], [ 0, 249, 50, 255 ], [ 174, 249, 0, 255 ], [ 249, 100, 0, 255 ], [ 249, 0, 125, 255 ], [ 149, 0, 249, 255 ], [ 0, 0, 206, 255 ], [ 0, 185, 206, 255 ], [ 0, 206, 41, 255 ], [ 143, 206, 0, 255 ], [ 206, 82, 0, 255 ], [ 206, 0, 103, 255 ], [ 124, 0, 206, 255 ], [ 0, 0, 162, 255 ], [ 0, 145, 162, 255 ], [ 0, 162, 32, 255 ], [ 114, 162, 0, 255 ], [ 162, 65, 0, 255 ], [ 162, 0, 81, 255 ], [ 97, 0, 162, 255 ], [ 0, 0, 119, 255 ], [ 0, 107, 119, 255 ], [ 0, 119, 23, 255 ], [ 83, 119, 0, 255 ], [ 119, 47, 0, 255 ], [ 119, 0, 59, 255 ], [ 71, 0, 119, 255 ], [ 100, 100, 249, 255 ], [ 100, 234, 249, 255 ], [ 100, 249, 129, 255 ], [ 204, 249, 100, 255 ], [ 249, 159, 100, 255 ], [ 249, 100, 174, 255 ], [ 189, 100, 249, 255 ], [ 82, 82, 206, 255 ], [ 82, 193, 206, 255 ], [ 82, 206, 107, 255 ], [ 168, 206, 82, 255 ], [ 206, 131, 82, 255 ], [ 206, 82, 143, 255 ], [ 156, 82, 206, 255 ], [ 65, 65, 162, 255 ], [ 65, 152, 162, 255 ], [ 65, 162, 84, 255 ], [ 132, 162, 65, 255 ], [ 162, 104, 65, 255 ], [ 162, 65, 114, 255 ], [ 123, 65, 162, 255 ], [ 47, 47, 119, 255 ], [ 47, 112, 119, 255 ], [ 47, 119, 61, 255 ], [ 97, 119, 47, 255 ], [ 119, 76, 47, 255 ], [ 119, 47, 83, 255 ], [ 90, 47, 119, 255 ], [ 174, 174, 249, 255 ], [ 174, 242, 249, 255 ], [ 174, 249, 189, 255 ], [ 227, 249, 174, 255 ], [ 249, 204, 174, 255 ], [ 249, 174, 212, 255 ], [ 219, 174, 249, 255 ], [ 143, 143, 206, 255 ], [ 143, 199, 206, 255 ], [ 143, 206, 156, 255 ], [ 187, 206, 143, 255 ], [ 206, 168, 143, 255 ], [ 206, 143, 175, 255 ], [ 181, 143, 206, 255 ], [ 114, 114, 162, 255 ], [ 114, 157, 162, 255 ], [ 114, 162, 123, 255 ], [ 147, 162, 114, 255 ], [ 162, 132, 114, 255 ], [ 162, 114, 137, 255 ], [ 142, 114, 162, 255 ], [ 83, 83, 119, 255 ], [ 83, 115, 119, 255 ], [ 83, 119, 90, 255 ], [ 108, 119, 83, 255 ], [ 119, 97, 83, 255 ], [ 119, 83, 101, 255 ], [ 104, 83, 119, 255 ], [ 224, 224, 249, 255 ], [ 224, 247, 249, 255 ], [ 224, 249, 229, 255 ], [ 242, 249, 224, 255 ], [ 249, 234, 224, 255 ], [ 249, 224, 237, 255 ], [ 239, 224, 249, 255 ], [ 185, 185, 206, 255 ], [ 185, 204, 206, 255 ], [ 185, 206, 189, 255 ], [ 199, 206, 185, 255 ], [ 206, 193, 185, 255 ], [ 206, 185, 195, 255 ], [ 197, 185, 206, 255 ], [ 145, 145, 162, 255 ], [ 145, 160, 162, 255 ], [ 145, 162, 149, 255 ], [ 157, 162, 145, 255 ], [ 162, 152, 145, 255 ], [ 162, 145, 153, 255 ], [ 155, 145, 162, 255 ], [ 107, 107, 119, 255 ], [ 107, 118, 119, 255 ], [ 107, 119, 109, 255 ], [ 115, 119, 107, 255 ], [ 119, 112, 107, 255 ], [ 119, 107, 113, 255 ], [ 114, 107, 119, 255 ], [ 0, 0, 249, 255 ], [ 0, 224, 249, 255 ], [ 0, 249, 50, 255 ], [ 174, 249, 0, 255 ], [ 249, 100, 0, 255 ], [ 249, 0, 125, 255 ], [ 149, 0, 249, 255 ], [ 0, 0, 206, 255 ], [ 0, 185, 206, 255 ], [ 0, 206, 41, 255 ], [ 143, 206, 0, 255 ], [ 206, 82, 0, 255 ], [ 206, 0, 103, 255 ], [ 124, 0, 206, 255 ], [ 0, 0, 162, 255 ], [ 0, 145, 162, 255 ], [ 0, 162, 32, 255 ], [ 114, 162, 0, 255 ], [ 162, 65, 0, 255 ], [ 162, 0, 81, 255 ], [ 97, 0, 162, 255 ], [ 0, 0, 119, 255 ], [ 0, 107, 119, 255 ], [ 0, 119, 23, 255 ], [ 83, 119, 0, 255 ], [ 119, 47, 0, 255 ], [ 119, 0, 59, 255 ], [ 71, 0, 119, 255 ], [ 100, 100, 249, 255 ], [ 100, 234, 249, 255 ], [ 100, 249, 129, 255 ], [ 204, 249, 100, 255 ], [ 249, 159, 100, 255 ], [ 249, 100, 174, 255 ], [ 189, 100, 249, 255 ], [ 82, 82, 206, 255 ], [ 82, 193, 206, 255 ], [ 82, 206, 107, 255 ], [ 168, 206, 82, 255 ], [ 206, 131, 82, 255 ], [ 206, 82, 143, 255 ], [ 156, 82, 206, 255 ], [ 65, 65, 162, 255 ], [ 65, 152, 162, 255 ], [ 65, 162, 84, 255 ], [ 132, 162, 65, 255 ], [ 162, 104, 65, 255 ], [ 162, 65, 114, 255 ], [ 123, 65, 162, 255 ], [ 47, 47, 119, 255 ], [ 47, 112, 119, 255 ], [ 47, 119, 61, 255 ], [ 97, 119, 47, 255 ], [ 119, 76, 47, 255 ], [ 119, 47, 83, 255 ], [ 90, 47, 119, 255 ], [ 174, 174, 249, 255 ], [ 174, 242, 249, 255 ], [ 174, 249, 189, 255 ], [ 227, 249, 174, 255 ], [ 249, 204, 174, 255 ], [ 249, 174, 212, 255 ], [ 219, 174, 249, 255 ], [ 143, 143, 206, 255 ], [ 143, 199, 206, 255 ], [ 143, 206, 156, 255 ], [ 187, 206, 143, 255 ], [ 206, 168, 143, 255 ], [ 206, 143, 175, 255 ], [ 181, 143, 206, 255 ], [ 114, 114, 162, 255 ], [ 114, 157, 162, 255 ], [ 114, 162, 123, 255 ], [ 147, 162, 114, 255 ], [ 162, 132, 114, 255 ], [ 162, 114, 137, 255 ], [ 142, 114, 162, 255 ], [ 83, 83, 119, 255 ], [ 83, 115, 119, 255 ], [ 83, 119, 90, 255 ], [ 108, 119, 83, 255 ], [ 119, 97, 83, 255 ], [ 119, 83, 101, 255 ], [ 104, 83, 119, 255 ], [ 224, 224, 249, 255 ], [ 224, 247, 249, 255 ], [ 224, 249, 229, 255 ], [ 242, 249, 224, 255 ], [ 249, 234, 224, 255 ], [ 249, 224, 237, 255 ], [ 239, 224, 249, 255 ], [ 185, 185, 206, 255 ], [ 185, 204, 206, 255 ], [ 185, 206, 189, 255 ], [ 199, 206, 185, 255 ], [ 206, 193, 185, 255 ], [ 206, 185, 195, 255 ], [ 197, 185, 206, 255 ], [ 145, 145, 162, 255 ], [ 145, 160, 162, 255 ], [ 145, 162, 149, 255 ], [ 157, 162, 145, 255 ], [ 162, 152, 145, 255 ], [ 162, 145, 153, 255 ], [ 155, 145, 162, 255 ], [ 107, 107, 119, 255 ], [ 107, 118, 119, 255 ], [ 107, 119, 109, 255 ], [ 115, 119, 107, 255 ], [ 119, 112, 107, 255 ], [ 119, 107, 113, 255 ], [ 114, 107, 119, 255 ], [ 0, 0, 249, 255 ], [ 0, 224, 249, 255 ], [ 0, 249, 50, 255 ], [ 174, 249, 0, 255 ], [ 249, 100, 0, 255 ], [ 249, 0, 125, 255 ], [ 149, 0, 249, 255 ], [ 0, 0, 206, 255 ], [ 0, 185, 206, 255 ], [ 0, 206, 41, 255 ], [ 143, 206, 0, 255 ], [ 206, 82, 0, 255 ], [ 206, 0, 103, 255 ], [ 124, 0, 206, 255 ], [ 0, 0, 162, 255 ], [ 0, 145, 162, 255 ], [ 0, 162, 32, 255 ], [ 114, 162, 0, 255 ], [ 162, 65, 0, 255 ], [ 162, 0, 81, 255 ], [ 97, 0, 162, 255 ], [ 0, 0, 119, 255 ], [ 0, 107, 119, 255 ], [ 0, 119, 23, 255 ], [ 83, 119, 0, 255 ], [ 119, 47, 0, 255 ], [ 119, 0, 59, 255 ], [ 71, 0, 119, 255 ], [ 100, 100, 249, 255 ], [ 100, 234, 249, 255 ], [ 100, 249, 129, 255 ], [ 0, 249, 50, 255 ] ]
    color_mapping = {
        label: "#{:02X}{:02X}{:02X}".format(*original_colormap[index][0:3])
        for label, index in labels.items()
    }
    return label_mapping, color_mapping

def convert_mask_to_xml_or_json(
    mask_path: Path,
    output_folder: Path,
    processing_spacing: float,
    label_mapping: tuple = (),
    color_mapping: tuple = (),
    dilation_iterations: int = 0,
    erose_iterations: int = 0,
    exclude_holes: bool = True,
    mask_wsi_spacing_ratio: float = 1,
    simplify=None,
    union=False,
    filename_tail="",
    verbose=True,
    write_additional_json=False,
    overwrite=False,
    ret=False
):
    inv_label_map = {value:name.lower() for value, name in label_mapping.items()}
    color_map = {name.lower():color for name, color in color_mapping.items()}
    
    if not mask_path.exists():
        raise ValueError(f"Mask path {mask_path} does not exists")

    if mask_path.is_dir():
        mask_paths = list(mask_path.glob('*.tif'))
    else:
        mask_paths = [mask_path]
    
    for mask_path in tqdm(mask_paths):
        print('processing', mask_path)
        output_path = output_folder / (mask_path.stem + filename_tail)
        
        output_path_xml = output_path.with_suffix('.xml')
        output_path_json = output_path.with_suffix('.json')
        
        output_path_xml_exists = output_path_xml.exists()
        output_path_json_exists = output_path_json.exists()
        
        if not overwrite and output_path_xml_exists and (output_path_json_exists if write_additional_json else True):
            print(f'Output file(s) already exist: {output_path_xml}{f" and {str(output_path_json)}" if write_additional_json else ""}')
            if ret:
                print('ret == True, quitting optional loop and returning: None, None')
                return None, None
            continue
        
        if verbose:
            print('\tLoading files')
        mask = WholeSlideImage(mask_path, backend="asap")
        mask_slide = mask.get_slide(processing_spacing).squeeze()
        ratio = mask.get_downsampling_from_spacing(processing_spacing) * mask_wsi_spacing_ratio
        
        if verbose:
            print('\tMaking polygons from mask')

        polygons = cv2_polygonize_with_hierarchy(
            mask_slide,
            dilation_iterations=dilation_iterations,
            erose_iterations=erose_iterations,
            exclude_holes=exclude_holes,
            values=list(inv_label_map),
            inv_label_map=inv_label_map
        )

        for value, polys in polygons.items():
            for poly_idx, poly in enumerate(polys):
                polygons[value][poly_idx] = geometry.Polygon(poly)

        if simplify:
            if verbose:
                print('\tSimplifying polygons')
            polygons = {k: [v.simplify(simplify) for v in v_list] for k, v_list in polygons.items()}
        if union:
            if verbose:
                print('\tTaking union of polygons')
            polygons = {k:unary_union(v) if k!=0 else v for k, v in polygons.items()}
    
        if verbose:
            print('\tMaking annotations from polygons')
        annotations = convert_polygons_to_annotations(
            polygons=polygons, inv_label_map=inv_label_map, color_map=color_map
        )
            
        if verbose:
            print('\tWriting XML')
            print('\t\tRatio', ratio)
            print('\t\tWriting to:', output_path_xml)
        write_asap_annotation(annotations=annotations, output_path=output_path_xml, color_map=color_map, scaling=ratio)
        
        if write_additional_json:
            if verbose:
                print('\tWriting JSON')
                print('\t\tWriting to:', output_path_json)
            annotations_json = convert_annotations_to_json(annotations, scaling=ratio)
            write_json_annotations(output_path_json, annotations_json)
            
        if ret:
            print('ret == True, quitting optional loop and returning: polygons, annotations')
            return polygons, annotations

def parse_labels(arg):
    try:
        labels = literal_eval(arg)
        if not isinstance(labels, dict):
            raise ValueError("Labels must be a dictionary.")
        return labels
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError("Invalid labels format. Please provide a valid dictionary.")


def example_usage():
    # EXAMPLE specific settings
    mask_path = "" # can be a file or folder where it seached for alld .tif files
    output_folder = "" # folder where the output will be written to
    labels={'Background':0,
        'Tumor': 1, 
        'Stroma': 3, 
        'Inflammation': 4, 
        'Healthy parenchyma': 5, 
        'Fatty tissue': 6, 
        'Necrotic tissue': 7, 
        'Erytrocytes': 8, 
        'Healthy epithelium': 9, 
        'Mucus': 10, 
        'Cartilage': 11,
        'Macrophages': 12,
        'Other': 13,
       }
    wsi_spacing = 0.25 # smallest spacing at which the wsi was scanned
    mask_spacing = 0.5 # spacing at which the input mask was made

    # IO related settings
    filename_tail = f'_spacing{processing_spacing}_simplify{str(simplify).replace(".", "")}{"_union" if union else ""}{"_EXCLUDE_holes" if exclude_holes else ""}'
    write_additional_json = True # jsons are smaller in size and fater during loading, but they are not supported by WSI viewers such as ASAP
    overwrite = False
    
    # Default settings
    label_mapping, color_mapping = labels_to_label_and_color_mapping(labels)
    mask_wsi_spacing_ratio = mask_spacing / wsi_spacing
    dilation_iterations = 0 # old and not used
    erose_iterations = 0 # old and not used
    exclude_holes=True # this excludes holes, which whole slide data does not support
    
    # Preference settings
    processing_spacing = 8 # this decides on which spacing the mask is read, deciding largely the precision of the polygons and the filesize of the output
    simplify=None # this simplifies the polygons, decreasing the size of the output files, None means no simplification, advised is 0.5 (slight simplification) to 8 for courser masks
    union=False # taking the union of the polygons, this is useful for merging the exteriors of overlapping polygons, but will also fill holes if the exteriours form a closed loop

    # Debugging settings
    ret = False # set this to true to make the function return the polygons and annotations, for debugging/output checking purposes 

    # RUN
    if ret == False:
        convert_mask_to_xml_or_json(
            mask_path=Path(mask_path),
            output_folder=Path(output_folder),
            processing_spacing=processing_spacing,
            label_mapping=label_mapping,
            color_mapping=color_mapping,
            dilation_iterations=dilation_iterations,
            erose_iterations=erose_iterations,
            exclude_holes=exclude_holes, 
            mask_wsi_spacing_ratio=mask_wsi_spacing_ratio,
            simplify=simplify,
            union=union,
            write_additional_json=write_additional_json,
            filename_tail=filename_tail,
            overwrite=overwrite
        )
    
    if ret == True:
        polygons, annotations = convert_mask_to_xml_or_json(
            mask_path=Path(mask_path),
            output_folder=Path(str(output_folder)),
            processing_spacing=processing_spacing,
            label_mapping=label_mapping,
            color_mapping=color_mapping,
            dilation_iterations=dilation_iterations,
            erose_iterations=erose_iterations,
            exclude_holes=exclude_holes, 
            mask_wsi_spacing_ratio=mask_wsi_spacing_ratio,
            simplify=simplify,
            union=union,
            write_additional_json=write_additional_json,
            filename_tail=filename_tail,
            overwrite=overwrite,
            ret=True,
        )
        return polygons, annotations


def main():
    parser = argparse.ArgumentParser(description='Script that converts masks to xml (and optionally json) annotations. Ensures correct loading of holes in annotations using WholeSlideData, and reduces filesize')
    
    # IO related settings
    parser.add_argument('--mask_path', type=str, help='Path to the mask file or folder where it will search for .tif files')
    parser.add_argument('--output_folder', type=str, help='Output folder path')

    # Data specific settings
    parser.add_argument('--labels', type=parse_labels, help='Labels as a dictionary. For example: --labels \'"Background": 0, "Tumor": 1, "Stroma": 3\'')    
    parser.add_argument('--wsi_spacing', type=float, help='Smallest spacing at which the WSI was scanned (for example 0.25). This together with the mask_spacing will make sure the coordnates of your output line up with the original WSI')
    parser.add_argument('--mask_spacing', type=float, help='Spacing at which the input mask was made. Whis together with the wsi_spacing will make sure the coordnates of your output line up with the original WSI')
    
    # Preference settings
    parser.add_argument('--processing_spacing', type=int, help='The spacing on which the mask will be read and processed. This decides largely the precision of the polygons and the filesize of the output')
    parser.add_argument('--simplify', type=float, default=0.5, help='# This simplifies the polygons, decreasing the size of the output files, None means no simplification, advised is 0.5 (slight simplification) to 8 for courser masks')
    parser.add_argument('--write_additional_json', action='store_true', default=True, help='Write additional JSON files. JSONs are faster during training')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
        
    args = parser.parse_args()
    
    # Default settings
    label_mapping, color_mapping = labels_to_label_and_color_mapping(args.labels)
    mask_wsi_spacing_ratio = args.mask_spacing / args.wsi_spacing
    filename_tail = f'_spacing{args.processing_spacing}_simplify{str(args.simplify).replace(".", "")}'

    convert_mask_to_xml_or_json(
        mask_path=Path(args.mask_path),
        output_folder=Path(args.output_folder),
        processing_spacing=args.processing_spacing,
        label_mapping=label_mapping,
        color_mapping=color_mapping,
        dilation_iterations=0,
        erose_iterations=0,
        exclude_holes=True, 
        mask_wsi_spacing_ratio=mask_wsi_spacing_ratio,
        simplify=args.simplify,
        union=False,
        write_additional_json=args.write_additional_json,
        filename_tail=filename_tail,
        overwrite=args.overwrite,
        ret=False,
    )

if __name__ == '__main__':
    main()