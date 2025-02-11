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
| `make lock`   | Relock dependencies |

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
