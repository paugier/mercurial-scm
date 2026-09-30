# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# taken from https://github.com/executablebooks/myst-nb
# see also https://github.com/executablebooks/sphinx-book-theme/blob/master/docs/conf.py

import os
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent / "_ext"))

# has to be imported before any Mercurial module
from hg_help_pages import mercurial_version

project = "Mercurial"
copyright = "2025, Mercurial developers"
author = "Mercurial developers"
release = mercurial_version()

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
    # generates the pages of `hg help` in source/help
    "hg_help_pages",
    "sphinx_hg",
    # lists the release notes, the older ones on an archive page
    "relnotes_toctree",
    "ablog",
]

# number of release notes listed in the menu
relnotes_recent = 10

templates_path = ["_templates"]
exclude_patterns = []

smartquotes = False

news_sidebars = [
    "navbar-logo.html",
    "icon-links.html",
    "ablog/categories.html",
    "ablog/tagcloud.html",
    "ablog/archives.html",
]
html_sidebars = {
    "news": news_sidebars,
    "news/**": news_sidebars,
}

# No "amsmath" and "dollarmath": there are no equations in the website, while
# there are many `$` which would be understood as such.
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
    "linkify",
]
myst_heading_anchors = 5

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
html_favicon = "_static/logo-droplets.svg"

html_theme_options = {
    "repository_url": "https://foss.heptapod.net/mercurial/hg-website",
    "repository_branch": "branch/default",
    "use_repository_button": True,
    "repository_provider": "gitlab",
    "path_to_docs": "",
    "toc_title": "On this page",
    "logo": {
        "image_light": "_static/logo-square-light.svg",
        "image_dark": "_static/logo-square-dark.svg",
    },
    "use_download_button": False,
    # "announcement": "This new Mercurial website is a work in progress!",
    # "home_page_in_toc": True,
    # "show_navbar_depth": 1,
    # "use_edit_page_button": True,
    # "navigation_with_keys": False,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["hg-custom.css"]
html_js_files = ["version-icon.js"]
# the sources of the pages are in the repository
html_copy_source = False
html_show_sourcelink = False

# copybutton_selector = "div:not(.output) > div.highlight pre"

myst_linkify_fuzzy_links = False

# -- ABlog ---------------------------------------------------

# taken and adapted from https://github.com/choldgraf/choldgraf.github.io

blog_baseurl = ""
blog_title = "Mercurial"
blog_path = "news"
blog_post_pattern = "news/*/*"
blog_feed_fulltext = True
blog_feed_subtitle = "Versioning"
fontawesome_included = True
post_redirect_refresh = 1
post_auto_image = 1
post_auto_excerpt = 2


def register_blog_posts(app):
    """Register the posts before ablog generates the pages of the news.

    ablog only registers the posts when a page is written. When nothing
    changed since the previous build, no page is written and the pages listing
    the posts, which are always generated, would be empty.
    """
    from ablog.blog import Blog
    from ablog.post import register_posts

    if not Blog(app):
        register_posts(app)
    return []


def setup(app):
    # has to run before the handler of ablog for this event (priority 500)
    app.connect("html-collect-pages", register_blog_posts, priority=100)
