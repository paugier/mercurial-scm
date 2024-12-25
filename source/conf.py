# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from util_hg_website import prepare_source

prepare_source()

project = "Mercurial"
copyright = "2024, Mercurial developers"
author = "Mercurial developers"
release = "6.9"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_book_theme",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = []


myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]

# nb_custom_formats = {".Rmd": ["jupytext.reads", {"fmt": "Rmd"}]}
nb_execution_mode = "cache"
nb_execution_show_tb = "READTHEDOCS" in os.environ
nb_execution_timeout = 60  # Note: 30 was timing out on RTD
# nb_ipywidgets_js = {
#     "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js": {
#         "integrity": "sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=",
#         "crossorigin": "anonymous",
#     },
#     "https://cdn.jsdelivr.net/npm/@jupyter-widgets/html-manager@*/dist/embed-amd.js": {
#         "data-jupyter-widgets-cdn": "https://cdn.jsdelivr.net/npm/",
#         "crossorigin": "anonymous",
#     },
# }
# nb_render_image_options = {"width": "200px"}
# application/vnd.plotly.v1+json and application/vnd.bokehjs_load.v0+json
suppress_warnings = ["mystnb.unknown_mime_type"]

# intersphinx_mapping = {
#     "python": ("https://docs.python.org/3.8", None),
#     # "jb": ("https://jupyterbook.org/", None),
#     # "myst": ("https://myst-parser.readthedocs.io/en/latest/", None),
#     # "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
#     # "nbclient": ("https://nbclient.readthedocs.io/en/latest", None),
#     # "nbformat": ("https://nbformat.readthedocs.io/en/latest", None),
#     # "sphinx": ("https://www.sphinx-doc.org/en/master", None),
# }
# intersphinx_cache_limit = 5


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_title = ""
html_theme = "sphinx_book_theme"
html_logo = "_static/mercurial-logo.png"
# html_favicon = "_static/logo-square.svg"
# html_theme_options = {
#     # "github_url": "https://github.com/executablebooks/myst-nb",
#     # "repository_url": "https://github.com/executablebooks/myst-nb",
#     "repository_branch": "branch/default",
#     "home_page_in_toc": True,
#     "path_to_docs": "docs",
#     "show_navbar_depth": 1,
#     "use_edit_page_button": True,
#     "use_repository_button": True,
#     "use_download_button": True,
#     # "launch_buttons": {
#     #     "binderhub_url": "https://mybinder.org",
#     #     "notebook_interface": "classic",
#     # },
#     "navigation_with_keys": False,
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# copybutton_selector = "div:not(.output) > div.highlight pre"
