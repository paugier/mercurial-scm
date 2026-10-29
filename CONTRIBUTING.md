# Contribute to hg-website

This version of the Mercurial website has been initiated in 2025. It is based on [Sphinx]
and uses [sphinx-book-theme] and [ablog]. Most content is written in .md files using the
[MyST] Markdown syntax.

The repository is hosted on https://foss.heptapod.net/mercurial/hg-website.

If you only want to report an issue or file a feature request, see
[](./community.md#issue-trackers).

## Install and test locally

One needs to install [PDM] and `make`.

| commands      |                     |
| ------------- | ------------------- |
| `make`        | Local build         |
| `make format` | Format sources      |
| `make test`   | Run the tests       |
| `make lock`   | Relock dependencies |

## Advanced PDM usage

Occasionally the website needs to be upgraded. The current versions of the dependencies
are locked in `pdm.lock` file. Here's how to work with it safely:

- First see if there are any outdated packages: `pdm outdated`. You can also specify a
  package or a pattern (glob) of packages and `--include-sub` to also show
  sub-dependencies: `pdm outdated --include-sub sphinx*`.

- Then try updating and see if hg-website works correctly: `pdm update -G web ablog`. To
  also update sub-dependencies recursively, use `--update-eager`, and to see what would
  be updated without installing anything, use `--dry-run`:
  `pdm update -G web ablog --update-eager --dry-run`.

- To update some packages to a release candidate, use `--prerelease` flag:
  `pdm update --prerelease -G web mercurial`.

Also useful:

- To see what depends on a package, try `pdm list --tree --reverse lxml`.

- To update all packages, try `pdm update --update-all`.

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

## Incremental builds

`make` only builds what changed since the previous build, and gives the same website as a
build from scratch (see `source/_ext/incremental_build.py`): when something shown by all
the pages changes, like a title or the tags of a post, all the pages are written again,
and what is not part of the website anymore is removed. If the result looks wrong anyway,
`make clean` then `make` builds everything again.

## Sending changes

This project uses basically the same workflow as Mercurial itself: see
[Contributing through Heptapod](./heptapod.md) for a more thorough overview.

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
