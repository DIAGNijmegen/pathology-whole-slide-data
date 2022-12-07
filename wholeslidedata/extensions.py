from sourcelib.extension import Extension, create_extensions_mapping

MIRX_EXTENSION = Extension((".mrxs",), folder_coupled=True)
TAGGED_IMAGE_FILE_EXTENSION = Extension((".tif", ".tiff"))
APERIO_SCAN_SCOPE_EXTENSION = Extension((".svs",))
HAMAMATSU_EXTENSION = Extension((".ndpi",))
EXTENSIBLE_MARKUP_LANGUAGE_EXTENSION = Extension((".xml",))
JAVA_SCRIPT_OBJECT_NOTATATION_EXTENSION = Extension((".json",))

WHOLE_SLIDE_IMAGE_EXTENSIONS = create_extensions_mapping(
    [
        MIRX_EXTENSION,
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
    ]
)
