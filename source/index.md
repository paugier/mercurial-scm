---
sd_hide_title: true
---

# Mercurial documentation

```{rubric} Work easier, Work faster
```

**Mercurial is a free, distributed source control management tool. It efficiently handles
projects of any size and offers an easy and intuitive interface.**

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
```{grid-item-card} It is fast and powerful

Mercurial efficiently handles projects of any size and kind. Every clone contains the whole project history, so most actions are local, fast and convenient. Mercurial supports a multitude of [workflows](https://www.mercurial-scm.org/wiki/WorkingPractices) and you can easily enhance its functionality with [extensions](https://www.mercurial-scm.org/wiki/UsingExtensions).

+++
[Learn more »](about.md)
```

```{grid-item-card} It is easy to learn

You can follow our simple guide to learn how to revision your documents with Mercurial, or just use the quick start to get going instantly. A short overview of Mercurial's decentralized model is also available.

+++
[Learn more »](learn.md)
```

```{grid-item-card} And it just works

Mercurial strives to deliver on each of its promises. Most tasks simply work on the first try and without requiring arcane knowledge.

+++
[Learn more »](learn.md)
```

````
______________________________________________________________________

```{toctree}
---
hidden:
maxdepth: 2
---
about.md
learn.md
```
