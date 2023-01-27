from wholeslidedata.image.backend import WholeSlideImageBackend
from importlib import import_module

class BackendNotAvailableError(ImportError):
    pass


class NonExistingBackendError(ValueError):
    pass


BACKENDS = {
    "tiffslide": ('wholeslidedata.interoperability.tiffslide.backend', 'TiffSlideImageBackend'),
    "asap": ("wholeslidedata.interoperability.asap.backend", "AsapWholeSlideImageBackend"),
    "pyvips": ("wholeslidedata.interoperability.pyvips.backend", "PyVipsImageBackend"),
    "cucim": ("wholeslidedata.interoperability.cucim.backend", "CucimWholeSlideImageBackend"),
    "openslide": ("wholeslidedata.interoperability.openslide.backend", "OpenSlideWholeSlideImageBackend"),
}


def get_backend(backend):
    if not isinstance(backend, str) and issubclass(backend, WholeSlideImageBackend):
        return backend

    try:
        module, attribute = BACKENDS[backend]
    except:
        raise NonExistingBackendError(backend)

    try:
        return getattr(import_module(module), attribute)
    except:
        raise BackendNotAvailableError(backend)
