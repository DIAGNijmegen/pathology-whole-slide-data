from sourcelib.extension import Extension, create_extensions_mapping


MIRX_EXTENSION = Extension((".mrxs",), folder_coupled=lambda path: path.with_suffix(""))
DICOM_EXTENSION = Extension((".dcm",), folder_coupled=lambda path: path.parent)
TAGGED_IMAGE_FILE_EXTENSION = Extension((".tif", ".tiff"))
APERIO_SCAN_SCOPE_EXTENSION = Extension((".svs",))
HAMAMATSU_EXTENSION = Extension((".ndpi",))
EXTENSIBLE_MARKUP_LANGUAGE_EXTENSION = Extension((".xml",))
JAVA_SCRIPT_OBJECT_NOTATATION_EXTENSION = Extension((".json",))
GEOJSON_EXTENSION = Extension((".geojson",))


WHOLE_SLIDE_IMAGE_EXTENSIONS = create_extensions_mapping(
    [
        MIRX_EXTENSION,
        DICOM_EXTENSION,
        TAGGED_IMAGE_FILE_EXTENSION,
        APERIO_SCAN_SCOPE_EXTENSION,
        HAMAMATSU_EXTENSION,
    ]
)

WHOLE_SLIDE_ANNOTATION_EXTENSIONS = create_extensions_mapping(
    [
        JAVA_SCRIPT_OBJECT_NOTATATION_EXTENSION,
        EXTENSIBLE_MARKUP_LANGUAGE_EXTENSION,
        TAGGED_IMAGE_FILE_EXTENSION,
        GEOJSON_EXTENSION
    ]
)
