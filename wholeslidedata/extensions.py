from pathlib import Path
from creationism.extension import Extension


class WholeSlideImageExtension(Extension):
    ...

class FolderCoupledExtension:    
    @classmethod
    def get_folder(cls, path):
        raise NotImplementedError()

@WholeSlideImageExtension.register((".mrxs",))
class MiraxExtension(WholeSlideImageExtension, FolderCoupledExtension):
    def get_folder(cls, path: Path):
        return path.with_suffix("")

@WholeSlideImageExtension.register((".tif", ".tiff",))
class TaggedImageFileExtension(WholeSlideImageExtension):
    ...


@WholeSlideImageExtension.register((".svs",))
class AperioScanScopeExtension(WholeSlideImageExtension):
    ...


@WholeSlideImageExtension.register((".ndpi",))
class HamamatsuExtension(WholeSlideImageExtension):
    ...

@WholeSlideImageExtension.register((".dcm",))
class DicomExtension(WholeSlideImageExtension, FolderCoupledExtension):
    def get_folder(cls, path: Path):
        return path.parent
    

class WholeSlideAnnotationExtension(Extension):
    ...


@WholeSlideAnnotationExtension.register((".xml",))
class ExtensibleMarkupLanguage(WholeSlideAnnotationExtension):
    ...

@WholeSlideAnnotationExtension.register((".json",))
class JavaScriptObjectNotation(WholeSlideAnnotationExtension):
    ...

@WholeSlideAnnotationExtension.register((".tif",))
class TaggedImageFileExtension(WholeSlideAnnotationExtension):
    ...