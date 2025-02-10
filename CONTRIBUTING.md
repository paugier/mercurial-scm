# Contribute to hg-website

## Install and test locally

One needs to install [PDM] and `make`.

| commands      |                     |
| ------------- | ------------------- |
| `make`        | Local build         |
| `make format` | Format sources      |
| `make lock`   | Relock dependencies |


## Sending changes

This project uses basically the same workflow as Mercurial itself: see https://wiki.mercurial-scm.org/Heptapod for a more thorough overview.

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

[pdm]: https://pdm-project.org
