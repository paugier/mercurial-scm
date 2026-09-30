# Contribute to hg-website

This version of the Mercurial website has been initiated in 2025. It is based on [Sphinx]
and uses [sphinx-book-theme] and [ablog]. Most content is written in .md files using the
[MyST] Markdown syntax.

The repository is hosted on https://foss.heptapod.net/mercurial/hg-website.

## Install and test locally

One needs to install [PDM] and `make`.

| commands      |                     |
| ------------- | ------------------- |
| `make`        | Local build         |
| `make format` | Format sources      |
| `make test`   | Run the tests       |
| `make lock`   | Relock dependencies |

## Size of the website

Once the pages are written, the build reduces what the readers have to download (see
`source/_ext/site_optimize.py`): the style sheets are gathered in a single one without
the rules that no page uses, the icon fonts only keep the icons in use, the dimensions of
the images are set and the files which are not used are removed.

- The class names that a script builds at runtime cannot be found: if some style is
  missing for an element created by a script, add a pattern matching its class to
  `site_optimize_safelist` in `source/conf.py`.
- Compress the images before adding them, photos rarely need more than 150 kB.
- `site_optimize = False` in `source/conf.py` disables all of this, which helps to tell
  if a problem comes from it.

## Sending changes

This project uses basically the same workflow as Mercurial itself: see
https://wiki.mercurial-scm.org/Heptapod for a more thorough overview.

Submit topic-based merge requests to https://foss.heptapod.net/mercurial/hg-website

Example:

```sh
hg pull
hg up default
hg topic improve-tuto
# edit files
make format
make
hg commit -m "tutorial: fix ..."
hg push
```

[ablog]: https://ablog.readthedocs.io
[myst]: https://mystmd.org/guide/syntax-overview
[pdm]: https://pdm-project.org
[sphinx]: https://www.sphinx-doc.org
[sphinx-book-theme]: https://sphinx-book-theme.readthedocs.io
