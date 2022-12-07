# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import sys
import os

# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'wholeslidedata'
copyright = '2021, Mart van Rijthoven'
author = 'Mart van Rijthoven'

# The full version, including alpha/beta/rc tags
release = '0.0.13'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

sys.path.insert(0, os.path.abspath('../../'))  # Source code dir relative to this file

extensions = [
    # 'sphinx.ext.autodoc',  # Core Sphinx library for auto html doc generation from docstrings
    # 'sphinx.ext.autosummary',  # Create neat summary tables for modules/classes/methods etc
    'sphinx.ext.viewcode',  # Add a link to the Python source code for classes, functions etc.
    'sphinx_copybutton',
    'sphinx_design',
    'nbsphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.todo',
]

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
add_module_names = False # Remove namespaces from class/method signatures
panels_add_bootstrap_css = False

html_theme_options = {
    # "use_edit_page_button": True,
    # "repository_url": "https://github.com/DIAGNijmegen/pathology-whole-slide-data",
    # "use_repository_button": True,
    # "use_issues_button": True,
    # "repository_branch": "main",
    # "path_to_docs": "./docs/source",
    # "extra_navbar": "<a href='./colophon.html'>Colophon</a>",
    # "launch_buttons": {
    #     "binderhub_url": "https://mybinder.org/"
    # },
    # 'navbar_links': [
    #     ("Examples", "examples"),
    #     ("Link", "http://example.com", True),
    # ],
    # # Render the next and previous page links in navbar. (Default: true)
    # 'navbar_sidebarrel': False,

    # # Render the current pages TOC in the navbar. (Default: true)
    # 'navbar_pagenav': False,
    "navbar_end": ["navbar-icon-links"],
    "show_prev_next": False,
    "header_links_before_dropdown": 7,
    "navbar_start": [],
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": "https://github.com/DIAGNijmegen/pathology-whole-slide-data",  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }
   ]

}


myst_enable_extensions = [
    # "dollarmath",
    # "amsmath",
    # "deflist",
    # "fieldlist",
    # "html_admonition",
    # "html_image",
    "colon_fence",
    # "smartquotes",
    # "replacements",
    # "strikethrough",
    # "substitution",
    # "tasklist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ['css/custom.css', 'css/default-theme.css']

html_title = "Whole-slide data"
jupyter_execute_notebooks = "off"


