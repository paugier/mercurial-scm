# hg-website

This is the Mercurial website. It uses the microframework flask to
serve jinja2 templates.

## Setup

To use this version of hg-website you need to install flask. This can be done with [PDM] by running:

```sh
pdm install
```

## Usage

To have flask serve the page, use:

```sh
pdm run ./hgwebsite.py
```

You can then visit <http://localhost:5000> to view the site.

[PDM]: https://pdm-project.org
