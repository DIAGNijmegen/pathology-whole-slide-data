import importlib
import json
import os
import pkgutil

from wholeslidedata import accessories


def import_accessories(module, module_name, verbose=False):
    for _, modname, ispkg in pkgutil.iter_modules(module.__path__):
        module_sub_name = module_name + f".{modname}"
        try:
            m = importlib.import_module(module_sub_name)
            if verbose:
                print(f"Loaded wsd accessory {module_sub_name}")
            if ispkg:
                import_accessories(m, module_sub_name, verbose=verbose)
        except (ImportError, OSError) as e:
            if verbose:
                print(f"---\nNot able to load: \n{module_sub_name}\nFrom: \n{module}\nError traceback: \n{e}\n---")
                


verbose = False
if "WSD_VERBOSE" in os.environ:
    verbose = json.loads(os.environ["WSD_VERBOSE"])

module_name = "wholeslidedata.accessories"
import_accessories(accessories, module_name, verbose=verbose)
