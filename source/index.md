---
sd_hide_title: true
---

# Mercurial documentation

`````{grid}
---
reverse:
gutter: 3 4 4 4
margin: 1 2 1 2
---
````{grid-item}
:columns: 12 4 4 4

```{image} _static/logo-hg.svg
:width: 150px
:class: sd-m-auto
```

````

````{grid-item}
:columns: 12 8 8 8
:child-align: justify
:class: sd-fs-5

```{rubric} Work easier, Work faster
```

Mercurial is a free, distributed source control management tool. It efficiently handles
projects of any size and offers an easy and intuitive interface.

````

`````

````{margin}
## Quick Start

*Clone a project and push changes*

```sh
hg clone https://www.mercurial-scm.org/repo/hello
cd hello
# (edit files)
hg add (new files)
hg commit -m 'My changes'
hg push
```

*Create a project and commit*

```sh
hg init (project-directory)
cd (project-directory)
# (add some files)
hg add
hg commit -m 'Initial commit'
```

````

______________________________________________________________________

```{rubric} How you can benefit from Mercurial
```

````{grid} 1 2 2 3
---
gutter: 1 1 1 2
---
```{grid-item-card} It is [fast and powerful](./about.md)

Mercurial efficiently handles [projects of any size and kind](./who.md). Every clone
contains the whole project history, so most actions are local, fast and convenient.
Mercurial supports a multitude of
[workflows](https://www.mercurial-scm.org/wiki/WorkingPractices) and you can easily
enhance its functionality with [extensions](https://www.mercurial-scm.org/wiki/UsingExtensions).

+++
[Learn more »](about.md)
```

```{grid-item-card} It is [easy to learn](./learn.md)

You can follow our simple [guide](./guide.md) to learn how to revision your documents
with Mercurial, or just use the [quick start](./quickstart.md) to get going instantly.
A short overview of Mercurial's decentralized model is also
[available](https://www.mercurial-scm.org/wiki/UnderstandingMercurial).

+++
[Learn more »](learn.md)
```

```{grid-item-card} And it just works

Mercurial strives to deliver on each of its promises. Most tasks simply work on the
first try and without requiring arcane knowledge.

+++
[Learn more »](https://foss.heptapod.net/mercurial/mercurial-devel/-/pipelines/95490)
```

````

______________________________________________________________________

```{toctree}
---
hidden:
maxdepth: 2
---
about.md
guide.md
install.md
Extensions <https://wiki.mercurial-scm.org/UsingExtensions>
news.md
Wiki <https://wiki.mercurial-scm.org/>
contribute.md
```

```{toctree}
---
caption: hg help
hidden:
maxdepth: 2
---
_generated/commands.md
_generated/topics.md
```
