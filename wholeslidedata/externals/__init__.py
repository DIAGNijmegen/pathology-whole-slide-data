import json
import os
import pkgutil

from wholeslidedata import externals


def load_externals(module, verbose=False):
    for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
        try:
            m = importer.find_module(modname).load_module(modname)
            if verbose:
                print(f"Loaded wsd external {m}")
            if ispkg:
                load_externals(m, verbose)
        except (ImportError, OSError) as e:
            if verbose:
                print(f"Not able to load {modname} from {module}:")
                print(e)


verbose = False
if "WSD_VERBOSE" in os.environ:
    verbose = json.loads(os.environ["WSD_VERBOSE"])

load_externals(externals, verbose=verbose)
