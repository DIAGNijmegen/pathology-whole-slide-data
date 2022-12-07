from functools import partial


class BackendNotAvailableError(Exception):
    pass


class NonExistingBackendError(Exception):
    pass


class NonAvailableBackend:
    def __init__(self, backend, *args, **kwargs):
        raise BackendNotAvailableError(backend)


try:
    from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
except:
    AsapWholeSlideImageBackend = partial(NonAvailableBackend, backend='asap')
try:
    from wholeslidedata.interoperability.pyvips.backend import PyVipsImageBackend
except:
    PyVipsImageBackend = partial(NonAvailableBackend, backend='pyvips')
try:
    from wholeslidedata.interoperability.cucim.backend import CucimWholeSlideImageBackend
except:
    CucimWholeSlideImageBackend = partial(NonAvailableBackend, backend='cucim')
try:
    from wholeslidedata.interoperability.openslide.backend import OpenSlideWholeSlideImageBackend
except:
    OpenSlideWholeSlideImageBackend = partial(NonAvailableBackend, backend='openslide')
try:
    from wholeslidedata.interoperability.tiffslide.backend import TiffSlideImageBackend
except:
    TiffSlideImageBackend = partial(NonAvailableBackend, backend='tiffslide')


BACKENDS = {
    "openslide": OpenSlideWholeSlideImageBackend,
    "asap": AsapWholeSlideImageBackend,
    "pyvips": PyVipsImageBackend,
    "tiffslide": TiffSlideImageBackend,
    "cucim": CucimWholeSlideImageBackend,
}


def get_backend(backend_name):
    try:
        return BACKENDS[backend_name]
    except:
        raise NonExistingBackendError(backend_name)