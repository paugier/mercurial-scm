# Contribute to hg-website

One needs to install [PDM] and `make`.

| commands      |                     |
| ------------- | ------------------- |
| `make`        | Local build         |
| `make format` | Format sources      |
| `make lock`   | Relock dependencies |

Submit topic based merge requests to https://foss.heptapod.net/mercurial/hg-website

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
