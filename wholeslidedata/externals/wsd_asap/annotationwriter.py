import xml.etree.cElementTree as ET
from pathlib import Path
from typing import List
from xml.dom import minidom

from wholeslidedata.annotation.structures import Point, Polygon
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation


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
        if (x, y) in coords_mem:
            continue
        coords_mem.append((x, y))

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
    for r in coordinates:
        x = r[0]
        y = r[1]
        coords_mem.append((x, y))
        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1


def write_point_set(annotations, output_path, label_name="tils", label_color="yellow"):
    # the root of the xml file.
    root = ET.Element("ASAP_Annotations")

    # writing each anno one by one.
    annos = ET.SubElement(root, "Annotations")

    # writing the last groups part
    anno_groups = ET.SubElement(root, "AnnotationGroups")

    index = 0
    anno = ET.SubElement(annos, "Annotation")
    anno.set("Name", "Annotation " + str(index))
    anno.set("Type", "PointSet")
    anno.set("PartOfGroup", label_name)
    anno.set("Color", label_color)

    coords = ET.SubElement(anno, "Coordinates")
    coords_mem = []
    ridx = 0
    for annotation in annotations:
        x, y = annotation.center
        coords_mem.append((x, y))

        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1

    group = ET.SubElement(anno_groups, "Group")
    group.set("Name", label_name)
    group.set("PartOfGroup", "None")
    group.set("Color", label_color)
    attr = ET.SubElement(group, "Attributes")

    # writing to the xml file with indentation
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_path, "w") as f:
        f.write(xmlstr)


def write_point_set2(points, output_path, label_name="detection"):
    # the root of the xml file.
    root = ET.Element("ASAP_Annotations")

    # writing each anno one by one.
    annos = ET.SubElement(root, "Annotations")

    # writing the last groups part
    anno_groups = ET.SubElement(root, "AnnotationGroups")

    index = 0
    anno = ET.SubElement(annos, "Annotation")
    anno.set("Name", "Annotation " + str(index))
    anno.set("Type", "PointSet")
    anno.set("PartOfGroup", label_name)
    anno.set("Color", "black")

    coords = ET.SubElement(anno, "Coordinates")
    coords_mem = []
    ridx = 0
    for point in points:
        x, y = point.x, point.y
        coords_mem.append((x, y))
        coord = ET.SubElement(coords, "Coordinate")
        coord.set("Order", str(ridx))
        coord.set("X", str(x))
        coord.set("Y", str(y))
        ridx += 1

    group = ET.SubElement(anno_groups, "Group")
    group.set("Name", label_name)
    group.set("PartOfGroup", "None")
    group.set("Color", "black")
    attr = ET.SubElement(group, "Attributes")

    # writing to the xml file with indentation
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_path, "w") as f:
        f.write(xmlstr)


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
        label_color = annotation.label.color if annotation.label.color is not None else "black"
        index = annotation.index
        if isinstance(annotation, Polygon):
            coordinates = annotation.coordinates / scaling
            write_polygon(annos, coordinates, index, label_name, label_color)
        elif isinstance(annotation, Point):
            coordinates = annotation.coordinates / scaling
            write_point(annos, [coordinates], index, label_name, label_color)
        else:
            raise ValueError("unsupported geometry", annotation)

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


def write_asap_annotation2(old_xml, annotations, output_path, scaling=1.0):
    # the root of the xml file.
    root = ET.Element("ASAP_Annotations")

    # writing each anno one by one.
    annos = ET.SubElement(root, "Annotations")

    # writing the last groups part
    anno_groups = ET.SubElement(root, "AnnotationGroups")

    labels = set()

    for annotation in annotations:
        label_name = annotation.label.name
        if label_name == "none":
            label_name = "None"
        if annotation.label.weight is not None and annotation.label.weight > 0:
            label_name = label_name + "-weight=" + str(annotation.label.weight)
        label_color = annotation.label.color if annotation.label.color else "black"
        index = annotation.index
        if isinstance(annotation, Polygon):
            coordinates = annotation.coordinates * scaling
            write_polygon(annos, coordinates, index, label_name, label_color)
        elif isinstance(annotation, Point):
            coordinates = annotation.coordinates * scaling
            write_point(annos, [coordinates], index, label_name, label_color)
        else:
            raise ValueError("unsupported geometry", annotation)

        labels.add((label_name, label_color))

    for elem in list(old_xml.getroot()[1]):
        group = ET.SubElement(anno_groups, "Group")
        group.set("Name", elem.attrib.get("Name").strip())
        group.set("PartOfGroup", elem.attrib.get("PartOfGroup").strip())
        group.set("Color", elem.attrib.get("Color").strip())
        ET.SubElement(group, "Attributes")

    # writing to the xml file with indentation
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_path, "w") as f:
        f.write(xmlstr)


def convert_annotations(input_folder, output_folder, scaling, suffix=""):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    xml_paths = input_folder.glob("*.xml")
    for xml_path in xml_paths:
        old_xml = ET.parse(xml_path)
        wsa = WholeSlideAnnotation(xml_path)
        output_path = output_folder / xml_path.name.replace(".xml", f"{suffix}.xml")
        print(f"Creating: {output_path}")
        write_asap_annotation2(old_xml, wsa.annotations, output_path, scaling)
