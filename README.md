# New Mercurial documentation website for 2025

The Mercurial project has a website (https://www.mercurial-scm.org) and a documentation
website (https://repo.mercurial-scm.org/hg/help). The website needs to be updated!

I (paugier) think Mercurial should have a new shiny and minimalist website (typically
like https://prefix.dev/) and a new documentation website based on modern Sphinx (with
Myst) (typically like https://pixi.sh/latest/).

This is the source of an attempt for a new documentation website using Sphinx.

Our target for the website is:

- quick overview of the main feature
- download link for the various platform
- documentation / tutorial
- information about hosting options, other supporting tools and commercial support options
- not being 15 year old
- maintainable, easy to modify.

Currently, the result of MR can be visualized in Gitlab pages with links as
<https://mercurial.pages.heptapod.net/hg-website/topic/default/with-sphinx>.

## Todo

- guide.md
- commands provided by extensions evolve
- setup https://mercurial-scm.readthedocs.io (advantage: readthedocs well referenced) ?
- issue disable "content" top right
