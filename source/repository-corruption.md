---
orphan: true
---

# Dealing with Repository and Dirstate Corruption

## Sources of corruption

Mercurial runs locally with normal user privileges without a protected store. This means
it's possible for regular users, their tools or their machines to damage their repository
history inadvertently. There are several possible sources of corruption, including:

- user error (damaging or deleting crucial files in `.hg/`)
- hardware failure (memory errors, disk corruption, power supply issues)
- operating system failure (filesystem bugs, kernel crashes, cross-platform compatibility
  issues)
- tool error (third-party tools inadvertently damaging `.hg/` state)
- Mercurial failure (bugs in `hg` causing data corruption - **very rare**)

User error is easily the most common of these. Mercurial has multiple levels of defense
against repository corruption including:

- append-only history for all core operations
- cryptographically strong hashes on all data
- journalled transactions
- frequent history duplication via clone/push/pull
- lightweight integrity checking via `verify`

As always, it's a good idea to maintain regular backups of critical data, for instance
via clones.

## Classes of corruption

There are two basic classes of corruption:

- [dirstate](https://wiki.mercurial-scm.org/DirState) corruption (Mercurial becomes
  confused about [WorkingDirectory](https://wiki.mercurial-scm.org/WorkingDirectory)
  state)

- [repository](https://wiki.mercurial-scm.org/Repository) corruption (`hg verify` reports
  errors in repository history)

Note that only damage to history should properly be referred to as 'repository
corruption', but we'll discuss both on this page anyway.

## Dirstate corruption

This occurs when the files tracking hg's notion of what you're currently working on
becomes damaged. The primary file here is `.hg/dirstate`. This file contains pointers to
the parent revision and information about all the files currently tracked in the working
directory. Corruption looks something like this:

```shell
$ hg st
M foo
A bar
$ hg id
58745409d2e2+ tip
#### DO NOT DO THIS ####
$ echo fdsjfkgsjdfhgskdfhkgshjkdfhjkgsjkhdfkhgjsdhjkfgoo > .hg/dirstate
#### DO NOT DO THIS ####
$ hg st
abort: unknown revision '6664736a666b67736a64666867736b6466686b67'!
```

Recovering from dirstate corruption is usually straightforward. If you know what revision
you're working on, you can run:

```shell
$ hg debugrebuildstate -r tip  # rebuild dirstate assuming we're at tip
$ hg id
58745409d2e2+ tip
$ hg st
M foo
? bar
```

Note that Mercurial still knows that `foo` is modified but has forgotten that `bar` was
added.

If `debugrebuildstate` doesn't work, it's usually possible to simply clone your
repository and get back to a working state (specify the `--pull` option to avoid
potential issues with hardlinks):

```shell
$ cd ..
$ hg clone --pull repo fixed-repo
requesting all changes
adding changesets
adding manifests
adding file changes
added 2 changesets with 2 changes to 1 files
updating to branch default
1 files updated, 0 files merged, 0 files removed, 0 files unresolved
$ cd fixed-repo
$ hg id
58745409d2e2+ tip
```

You can now copy over any changes from your damaged working directory to your repaired
one.

## Repository corruption

This is corruption that involves the project history, specifically the files in
`.hg/store`. This can happen in a number of ways, most often through user error (for
instance deleting all files with `foo.c` in their name). For example:

```shell
$ hg verify
checking changesets
checking manifests
crosschecking files in changesets and manifests
checking files
1213 files, 8591 changesets, 17158 total revisions

$ rm .hg/store/data/mercurial/error.py.i  # oops!
$ hg verify
checking changesets
checking manifests
crosschecking files in changesets and manifests
checking files
 data/mercurial/error.py.i@7633: missing revlog!
 7633: empty or missing mercurial/error.py
 mercurial/error.py@7633: f6aad9f78a08 in manifests not found
 mercurial/error.py@7636: 4fb29207f327 in manifests not found
 mercurial/error.py@7637: 3bfff9613e8b in manifests not found
 mercurial/error.py@7640: 40ee894622ad in manifests not found
 mercurial/error.py@7641: e640820306d6 in manifests not found
 mercurial/error.py@7643: f43c616251f5 in manifests not found
 mercurial/error.py@7644: 455d738b74c7 in manifests not found
 mercurial/error.py@7646: a3128b43b03f in manifests not found
 mercurial/error.py@7947: b4a8b72bfa1c in manifests not found
 mercurial/error.py@8144: 1f996809c441 in manifests not found
 mercurial/error.py@8225: e1537136a8d0 in manifests not found
 mercurial/error.py@8226: 5f91269779c0 in manifests not found
 mercurial/error.py@8227: 6706abc98ab2 in manifests not found
1213 files, 8591 changesets, 17145 total revisions
15 integrity errors encountered!
(first damaged changeset appears to be 7633)
```

### Basic recovery

> ⚠️ **Caution**: Make a backup before attempting repository repair!

Here, we've damaged our repository starting at revision 7633 (see the line at the
bottom). Taking advantage of the append-only property of Mercurial, we can recover
everything up to this point with:

```shell
$ cd ..
$ hg clone -r 7632 damage fixed
requesting all changes
adding changesets
adding manifests
adding file changes
added 7633 changesets with 14944 changes to 1126 files
updating to branch default
964 files updated, 0 files merged, 0 files removed, 0 files unresolved
$ cd fixed
$ hg verify
checking changesets
checking manifests
crosschecking files in changesets and manifests
checking files
1126 files, 7633 changesets, 14944 total revisions
```

### Rebuilding from known-good sources

We can also use `pull -r` to incrementally attempt to pull larger portions of the history
into a repository that has some of the missing file revisions. It may also be possible to
copy intact copies of the damaged revlog files from a clone.

### Reconstructing missing revlogs

Occasionally, a revlog containing a single revision becomes damaged. This is relatively
easy to manually reconstruct if you still have an **exact copy** of that file revision
(let's assume it is in `mybackuplocation` which we will use below). For instance,
consider a repo named `broken` where the revlog `f2.i` in the project root has gone
missing:

```shell
$ hg verify
checking changesets
checking manifests
crosschecking files in changesets and manifests
checking files
 data/f2.i@1: missing revlog!
 1: empty or missing f2
 f2@1: 5266937d3e5f in manifests not found
3 files, 3 changesets, 2 total revisions
3 integrity errors encountered!
(first damaged changeset appears to be 1)
```

Note that `@1` means that the missing revlog is referenced in changeset `1`. To
reconstruct this file we need make a new repository to recreate the conditions of that
commit. (When cloning, you may need to modify the clone command to ensure the new
repository has the same [repository format](missing-requirement.md#repository-formats) as
the existing one.)

```shell
$ cd ..
$ hg clone -r 0 broken fix # damaged revision minus 1
$ cd fix
$ cp <mybackuplocation>/f2 f2
$ hg add f2
$ hg ci -m fix f2
```

Now we've created a new `f2.i` that has a single revision that's marked as being in
changeset 1. We should be able to copy this back to the `broken` repo:

```shell
$ cp .hg/store/data/f2.i ../broken/.hg/store/data/f2.i
$ cd ../broken
$ hg verify
checking changesets
checking manifests
crosschecking files in changesets and manifests
checking files
3 files, 3 changesets, 3 total revisions
```

> **Note**: You may need to edit `.hg/store/fncache` to get verify to see your
> reintroduced file.

This process can also be extended to repair corrupted revisions in revlogs.

### Recovery using the `convert` extension

Alternatively, you can try to use the `convert` extension to force a rebuild of the
repository. Be forewarned that this will result in new hashes for all revisions and will
require **all users to re-clone from the recovered repository**.

First step is to enable the `convert` extension, assuming the repository is in the
directory named `REPO`:

```shell
$ vim REPO/.hg/hgrc
...
[extensions]
hgext.convert=
...
```

While it is possible to convert in-place, a wise safety precaution is to convert to an
empty directory:

```shell
$ mkdir REPOFIX
```

Use the `convert` extension to recover the repository:

```shell
$ hg convert --config convert.hg.ignoreerrors=True REPO REPOFIX
scanning source...
sorting...
converting...
[Various messages, most of which will be the commit messages]
ignoring: data/.DS_Store.i@26a47e9188c: no match found
[More commit messages]
.hgtags@78ff9079978f, line 1: tag '1.0b1' refers to unknown node
updating tags
```

The output from your command will vary greatly, but the important part is that the
corrupted files have been ignored and the rest of the files are in the new repository.

> **Note** If you still get abort, you can work around the problem by deleting
> `.hg/store/data/{corrupted-file}.i`. Make a backup before attempting to modify
> repositories.

## Advanced: inspecting repository data structures

Mercurial's internal data structures are fairly easy to understand. Details can be found
at [Design](https://wiki.mercurial-scm.org/Design) and in
[FileFormats](https://wiki.mercurial-scm.org/FileFormats). Mercurial includes commands
for directly dumping most aspects of its internals via commands like `debugindex`,
`debugdata`, `debugstate` (see
[DebuggingFeatures](https://wiki.mercurial-scm.org/DebuggingFeatures)).

## See also

- [HardlinkedClones](https://wiki.mercurial-scm.org/HardlinkedClones)
