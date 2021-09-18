from creationism.extension import Extension


class WholeSlideImageExtension(Extension):
    ...

class FolderCoupledExtension:
    ...

@WholeSlideImageExtension.register((".mrxs",))
class MiraxExtension(WholeSlideImageExtension, FolderCoupledExtension):
    ...

@WholeSlideImageExtension.register((".tif", ".tiff",))
class TaggedImageFileExtension(WholeSlideImageExtension):
    ...


@WholeSlideImageExtension.register((".svs",))
class AperioScanScopeExtension(WholeSlideImageExtension):
    ...


@WholeSlideImageExtension.register((".ndpi",))
class HamamatsuExtension(WholeSlideImageExtension):
    ...


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