---
sd_hide_title: true
---

# Guide

# Learning Mercurial in Workflows

With Mercurial you can use a multitude of different workflows. This page shows some of
them, including their use cases. It is intended to make it easy for beginners of version
tracking to get going instantly and learn completely incrementally. It doesn't explain
the concepts used, because there are already many other great resources doing that.

Alternatives to this guide and further reading:

- [Tutorial](https://www.mercurial-scm.org/wiki/Tutorial) - a more exhaustive tutorial.
- [Mercurial: The Definitive Guide](https://book.mercurial-scm.org/) - a very detailed
  description of Mercurial including
  [behind the scenes](https://book.mercurial-scm.org/read/concepts.html), an indepth
  article on the design of Mercurial.
- [Understanding Mercurial](https://www.mercurial-scm.org/wiki/UnderstandingMercurial) -
  the concepts behind Mercurial.

```{note}
This guide doesn't require any prior knowledge of version control systems (though
subversion users will likely feel at home quite quickly). Basic command line abilities
are helpful, because we'll use the command line client.
```

## Basic workflows

We go from simple to more complex workflows. Those further down build on previous
workflows.

### Log keeping

#### Use Case

The first workflow is also the easiest one: You want to use Mercurial to be able to look
back when you did which changes.

This workflow only requires an installed Mercurial and write access to some file storage
(you almost definitely have that 🙂). It shows the basic techniques for more complex
workflows.

#### Workflow

##### Prepare Mercurial

As first step, you should teach Mercurial your name. For that you open the file `~/.hgrc`
(or `mercurial.ini` in your home directory for Windows) with a text-editor and add the ui
section (user interaction) with your username:

```
[ui]
username = Mr. Johnson <johnson@smith.com>
```

##### Initialize the project

Now you add a new folder in which you want to work:

```sh
hg init project
```

##### Add files and track them

Enter the project folder, create some files, then add and commit them.

```sh
cd project
echo 'print("Hello")' > hello.py
hg add
hg commit
```

(your default editor opens, enter the commit message, save and close.)

output of hg add:

```
adding hello.py
```

display of hg commit (with your message):

```
Initial commit.

HG: Enter commit message.  Lines beginning with 'HG:' are removed.
HG: Leave message empty to abort commit.
HG: --
HG: user: Mr. Johnson <johnson@smith.com>
HG: branch 'default'
HG: added hello.py
```

````{note}
To avoid switching to an editor, you can also enter the commit message on the command-line:

```sh
hg commit -m "[MESSAGE]"
```

````

You can then look into your initial history with hg log:

```sh
hg log
```

output of hg log:

```
changeset:   0:a5ecbf5799c8
user:        Mr. Johnson
date:        Sun Nov 20 11:00:00 2011 +0100
summary:     Initial commit.
```

````{note}
By default Log only shows the first line of the commit message. To show the full message, use

```
hg log -v
```
````

````{note}
You can also go into an existing directory with files and init the repository there.

```
$ cd project
$ hg init
```
````

Also you can add only specific files instead of all files in the directory. Mercurial
will then track only these files and won't know about the others. The following tells
mercurial to track all files whose names begin with "file0" as well as file10, file11 and
file12.

```sh
hg add file0* file10 file11 file12
```

```{note}
We stop here but this page should soon be updated with up-to-date content.
```
