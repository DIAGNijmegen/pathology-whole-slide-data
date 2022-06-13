from wholeslidedata.annotation.structures import Point, Polygon
from wholeslidedata.labels import Label
from creationism.utils import open_json
import xml.etree.cElementTree as ET
from pathlib import Path
from xml.dom import minidom
import argparse
from wholeslidedata.image.wholeslideimage import WholeSlideImage
import click
import numpy as np





def write_polygon(annos, coordinates, index, label_name, label_color):
    anno = ET.SubElement(annos, "Annotation")
    anno.set("Name", "Annotation " + str(index))
    anno.set("Type", "Polygon")
    anno.set("PartOfGroup", label_name)
    anno.set("Color", label_color)

    coords = ET.SubElement(anno, "Coordinates")
    coords_mem = []
    ridx = 0
    for _, r in enumerate(coordinates):
        x = int(r[0])
        y = int(r[1])
        if (x,y) in coords_mem:
            continue
        coords_mem.append((x,y))

        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1


def write_point(annos, coordinates, index, label_name, label_color):
    anno = ET.SubElement(annos, "Annotation")
    anno.set("Name", "Annotation " + str(index))
    anno.set("Type", "Dot")
    anno.set("PartOfGroup", label_name)
    anno.set("Color", label_color)

    coords = ET.SubElement(anno, "Coordinates")
    coords_mem = []
    ridx = 0
    for _, r in enumerate(coordinates):
        x = int(r[0])
        y = int(r[1])
        if (x,y) in coords_mem:
            continue
        coords_mem.append((x,y))

        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1
        
def write_point_set(annos, points, index, label_name, label_color):
    anno = ET.SubElement(annos, "Annotation")
    anno.set("Name", "Annotation " + str(index))
    anno.set("Type", "PointSet")
    anno.set("PartOfGroup", label_name)
    anno.set("Color", label_color)

    coords = ET.SubElement(anno, "Coordinates")
    coords_mem = []
    ridx = 0
    for point in points:
        x, y = point[0]
        if (x,y) in coords_mem:
            continue
        coords_mem.append((x,y))

        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1
    
        
def write_asap_annotation(annotations, output_path, scaling=1.0):
    # the root of the xml file.
    root = ET.Element("ASAP_Annotations")

    # writing each anno one by one.
    annos = ET.SubElement(root, "Annotations")

    # writing the last groups part
    anno_groups = ET.SubElement(root, "AnnotationGroups")

    labels = set()

    for annotation in annotations:

        label_name = annotation.label.name
        if annotation.label.weight is not None and annotation.label.weight > 0:
            label_name = label_name + '-weight=' + str(annotation.label.weight)
        label_color = annotation.label.color if annotation.label.color else "black"
        index = annotation.index        
        if isinstance(annotation, Polygon):
            coordinates = annotation.coordinates
            write_polygon(annos, coordinates, index, label_name, label_color)
        elif isinstance(annotation, Point):
            coordinates = annotation.coordinates
            write_point(annos, [coordinates], index, label_name, label_color)
        else:
            raise ValueError('unsupported geometry', annotation)
            
        labels.add((label_name, label_color))

    for label, color in labels:
        group = ET.SubElement(anno_groups, "Group")
        group.set("Name", label)
        group.set("PartOfGroup", "None")
        group.set("Color", color)
        attr = ET.SubElement(group, "Attributes")

    # writing to the xml file with indentation
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_path, "w") as f:
        f.write(xmlstr)

@click.command()
@click.option("--image_path", type=Path, required=True)
@click.option("--annotation_path", type=Path, required=True)
@click.option("--spacing", type=float, required=True)
def main(image_path, annotation_path, spacing):
    wsi = WholeSlideImage(image_path, backend='asap')
    spacing = wsi.get_real_spacing(spacing)
    data = open_json(annotation_path)
    label = Label(name='lymphocyte', value=1, color='yellow')
    points = []
    for idx, point in enumerate(data['points']):
        point = (np.array(point['point'])*1000)/spacing
        p = Point(idx, label, [(point[0], point[1])])
        points.append(p)
    write_asap_annotation(points, str(annotation_path).replace('.json', '.xml'))
    
if __name__ == "__main__":
    main()
