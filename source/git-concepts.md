# Mercurial for Git users

[Git](https://git-scm.com) is a very popular Distributed SCM that works very similarly to
Mercurial. Both are built upon such similar concepts that most repositories can be
converted to and from Mercurial and Git without any significant data loss! There are,
however, significant design and conceptual differences that may cause trouble when coming
from Git to Mercurial.

## High-level Comparison

Mercurial and Git differ mainly in nomenclature, interface, and - of course -
implementation details, including features.

Mercurial has always focused heavily on interface aspects. This makes Mercurial easier to
learn - even for someone who has never used version control before. Git tends to expose
lower-level implementation details to users, requiring knowledge of them in order to use
Git effectively (e.g. refs). In comparison to Git, Mercurial requires a shallower
understanding to operate in a useful manner.

Mercurial is also safer by default: functionality like history rewriting (which is
considered an advanced topic for a version control newcomer) must be enabled. To
Mercurial newcomers with Git experience, this often gives the false appearance that
Mercurial is less powerful or featureful than it really is.

## Logical architecture

This section tries to prove that the only logical architecture difference between the two
systems, is nomenclature.

### History model

One of the first Git lessons is the repository basic object types: blob, tree and commit.
These are the building blocks for the history model. Mercurial also builds up history
upon the same three concepts, respectively: file,
[manifest](./help/topics/glossary.rst#manifest) and
[changeset](./help/topics/glossary.rst#changeset).

To identify these objects both systems use a SHA1 hash value, what Mercurial calls
[nodeid](/Nodeid). Additionally, Mercurial also provides a **local** revision number, a
simply incrementing integer, for each [changeset](./help/topics/glossary.rst#changeset),
in addition to the reverse count notation provided by Git (like HEAD~4). (Mercurial also
includes a powerful query language for specifying revisions called
[revsets](./help/topics/revisions.rst).)

From that, Mercurial's view of history is, just like Git's, a
[DAG](./help/topics/glossary.rst#dag) or Directed Acyclic Graph of changesets. For
instance, the graphical representation of history is the same in the two.

### Branch model

Also like in Git, Mercurial supports branching in different ways. First and foremost,
each clone of a repository represents a branch, potentially identical to other clones of
the same repositories. This way of branching is sometimes referred to as *heavy branches*
and works almost the same in both systems.

Then Git has its famous *lightweight branches*, which allow switching between development
lines within the same clone of a repository. Take the following history graph as an
example:

```{graphviz}
---
name: light branches
caption: Light branches example
---
digraph {
    rankdir = LR;
    node [shape=box];
    a -> b -> c [dir=back];
    c -> d -> e [dir=back];
    c -> f -> g [dir=back];
    e -> X [dir=back, style=dotted];
    g -> Y [dir=back, style=dotted];
    X [shape=cds, orientation=180];
    Y [shape=cds, orientation=180];
}
```

In Git, branches `X` and `Y` are simply references to the `e` and `g` commits. If a new
commit is appended to `e` then the reference `X` would point to such commit, like this:

```{graphviz}
---
name: moving reference
caption: Moving reference example
---
digraph {
    rankdir = LR;
    node [shape=box];
    a -> b -> c [dir=back];
    c -> d -> e -> h [dir=back];
    c -> f -> g [dir=back];
    h -> X [dir=back, style=dotted];
    g -> Y [dir=back, style=dotted];
    X [shape=cds, orientation=180];
    Y [shape=cds, orientation=180];
}
```

In Mercurial, the `X` and `Y` branches are called *heads* and they can be referred by
their changeset identifier: either local (number) or global (SHA1 hash). In brief, it is
like using Git detached heads instead of branch names, but much easier and without the
risk of garbage collection (see [](./help/commands/heads.rst)). They can be referred also
by a [bookmark](./help/topics/glossary.rst#bookmark), which can be pushed and pulled with
the `-B`/`--bookmark` option.

Finally, Mercurial has another branching functionality called
[NamedBranches](/NamedBranches), also known as long lived branches. This kind of branch
does not have a Git equivalent. For more information about named branches:

- [Branch](/Branch)

- [NamedBranches](/NamedBranches)

- [MultipleHeads](/MultipleHeads)

### Tag model

Like with branches both Git and Mercurial support two tag levels: *local* and *global*.
Local tags are only visible where they were created and do not propagate, so they behave
practically the same in both systems.

Global tags is one of the aspects that really differs from Git. Apparently they serve the
same purpose, however they are treated differently. In Git, global tags have a dedicated
repository object type; these tags are usually referred as *annotated tags*. In
Mercurial, though, they are stored in a special text file called `.hgtags` residing in
the root directory of a repository clone. Because the `.hgtags` file is versioned as a
normal file, all the file modifications are stored as part of the repository history.

Two important things need to be remembered about how `.hgtags` is handled:

1. The file only grows and should not be edited, except when it generates a merge
   conflict.

2. Because it is revision controlled, there is a corresponding
   [revlog](./help/topics/glossary.rst#revlog). When looking for tags, only the latest
   revision of `.hgtags` is parsed; never mind the checked out copy revision.

Although it is questioned by many people new to Mercurial, this design allows to keep
track of all global tagging operations. Nevertheless, it also confuses because it can
lead to some puzzling scenarios. For example, consider the following history graph:

```{graphviz}
---
name: global tag
caption: Global tag example
---
digraph {
    rankdir = LR;
    node [shape=box];
    a -> b -> c [dir=back];
    c -> T [dir=back, style=dotted];
    T [shape=cds, orientation=180];
    c -> "d: add tag T" -> e -> f [dir=back];
}
```

In the graph, `T` is a global tag pointing to changeset `c`. This tagging action
generated changeset `d` because `.hgtags` had to be committed. Now, if you clone a new
repository using `hg clone --rev T`, the history graph of the cloned repository would
look like this:

```{graphviz}
---
name: clone by global tag
caption: Clone by global tag example
---
digraph {
    rankdir = LR;
    node [shape=box];
    a -> b -> c [dir=back];
}
```

Therefore, in the new repository tag `T` does not exist. The reason behind this is
because in the original repository tag `T` points to changeset `c`; however, tag `T` is
added by commit `d` which is a descendant of `c`. As the clone command limits the history
up to changeset `c`, the addition of the tag is not included in the new repository.
Things work similarly when tagging a particular revision using `hg tag --rev ...`

Regarding tag propagation across repositories, Mercurial has very simple semantics. From
the history and [WireProtocol](/WireProtocol) point of view, the `.hgtags` file is
treated like the rest of the tracked files, which means that any global tagging operation
becomes visible to everyone just like any other commit. It also implies that merge
conflicts can occur in `.hgtags`.

The rationale behind Mercurial's global tags is briefly justified in
[this thread](https://www.mercurial-scm.org/pipermail/mercurial/2009-January/023271.html)
(January 2009).

See also:
[Giving a persistent name to a revision](http://hgbook.red-bean.com/read/managing-releases-and-branchy-development.html#id383990).

## Behavioral differences

In most design decisions, Mercurial tries to avoid exposing excessive complexity to the
user. This can sometimes lead to the belief that both systems have nothing in common when
in practice the difference is subtle, and vice versa. The main difference is that
mercurial does not offer an "undo" to what you did without using commands that are
referred to as "dangerous", "not what you want" etc in the help pages.

### Communication between repositories

While the branching model is very similar, moving history between different repositories
is slightly mismatched.

Git adds the notion of *tracking branch*, a branch that is used to follow changes from
another repository. Tracking branches allow to selectively pull or push branches from or
to a remote repository.

Mercurial keeps things simpler in this aspect:

- When you pull, you bring all remote heads into your local repository. Then you can
  decide whether to merge or not. Or else, pull and merge automatically using `-u`.

- All pushes that would create new heads (i.e. lightweight branches) stop with a warning,
  except if the user explicitly forces them.

### Git's staging area

Git is the only Distributed SCM that exposes the concept of *index* or *staging area*.
The others may implement and hide it, but in no other case is the user aware or has to
deal with it.

Mercurial's rough equivalent is the [DirState](/DirState), which controls working copy
status information to determine the files to be included in the next commit. But in any
case, this file is handled automatically. Additionally, it is possible to be more
selective at commit time either by specifying the files you want to commit on the command
line or by using `hg commit --interactive`.

If you felt uncomfortable dealing with Git's index, you are switching for the better. 😉

If you need the index, you can gain its behavior (with many additional options)
[with mercurial queues](http://stevelosh.com/blog/2010/08/a-git-users-guide-to-mercurial-queues)
([MQ](./help/extensions/mq.rst)). Simple addition of changes to the index can be imitated
by just building up a commit with `hg commit --amend` (optionally with `--secret`, see
[phases](./help/topics/phases.rst)).

### Bare repositories

Although this is a minor issue, Mercurial can obviously handle a *bare* repository; that
is, a repository **without** a working copy. In Git you need a configuration option for
that, whereas in Hg you only need to check out the `null` revision, like this:

```sh
hg update null
```

As push and pull operations do not update the working copy by default, by not updating
the working copy you get the same effect of a bare repository.
