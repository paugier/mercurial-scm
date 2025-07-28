---
orphan: true
---

# Missing Requirement

All about handling missing repository requirements.

## What is a missing requirement?

A repository stored on disk has some requirements. The requirements are listed in a file
\- that file is the first and most crucial file Mercurial reads before operating on the
repository.

Mercurial will fail with `abort: unknown repository format: requires features 'X'` if it
doesn't know and provide **all** the listed features. This mechanism was designed for
on-disk formats but is also used for extensions providing alternative high-level
semantics of the stored data.

## Repository formats

The support of repository formats is inherently tied to Mercurial versions. When an old
version of Mercurial attempts to read an on-disk repository using features it doesn't
support, it immediately aborts with a "requirement error" to avoid compatibility
problems.

This only happens when a newer version of Mercurial **creates** a repository via `init`
or `clone` and an older version is used to access that repository **on the same disk or
network filesystem**. All versions of Mercurial are compatible over HTTP or SSH
connections.

The following table shows which Mercurial versions support each requirement:

| **Requirement**           | **Compatible versions** | **Description**                                                                                                           |
| ------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `revlogv1`                | >= 0.9                  | Revlog v1 is used                                                                                                         |
| `store`                   | >= 0.9.2                | The directory `.hg/store` contains the subdirectories `data`                                                              |
| `fncache`                 | >= 1.1                  | store files are named to work around Windows limitations                                                                  |
| `shared`                  | >= 1.3                  | shared store support                                                                                                      |
| `dotencode`               | >= 1.7                  | Leading `.` (period) or ` ` (space) in store filenames are encoded https://www.mercurial-scm.org/repo/hg/rev/34d8247a4595 |
| `parentdelta`             | 1.7 - 1.8.4             | Use `parentdelta` for new revlogs (experimental, replaced by generaldelta)                                                |
| `generaldelta`            | >= 1.9                  | Use `generaldelta` for improved delta chaining                                                                            |
| `sparse-revlog`           | >= 4.7                  | For improved delta re-use inside revlogs                                                                                  |
| `revlog-compression-zstd` | >= 5.0                  | Use zstd instead of zlib (default) compression                                                                            |
| `persistent-nodemap`      | >= 5.5                  | persist nodemap index for changelog and manifestlog                                                                       |
| `share-safe`              | >= 5.7                  | safe behaviour for all shares that access a repository                                                                    |
| `dirstate-v2`             | >= 6.0                  | a more powerful dirstate format that allows for significant speed ups while used in combination with Rust                 |
| `internal-phase-2`        | >= 6.2                  | enable `internal` phase used initially by `shelve`                                                                        |

An "unknown repository format" abort can be resolved in different ways:

### Use a newer Mercurial

See the above table to find a version that supports the missing requirement. Upgrading is
generally painless, see
[UpgradingMercurial](https://wiki.mercurial-scm.org/UpgradingMercurial) for more
information.

### Downgrade your repository over the network

Because all versions of Mercurial can interoperate over the network, an old client can
simply pull from a repository served by a new client:

```
# run this on the new client
$ hg serve
listening at http://hostname:8000/ (bound to *:8000)

# run this on the old client
$ hg clone http://hostname:8000/ downgraded-repo
```

### Downgrade your repository with a new client

The [format configuration option](https://www.mercurial-scm.org/doc/hgrc.5.html#format)
configuration option may be used to instruct Mercurial to create older repository
formats. For example, to convert a `dotencode` repository into the previous format, the
command

```
hg --config format.dotencode=0 clone --pull repoA repoB
```

can be used, which of course requires a Mercurial version that supports the 'dotencode'
capability.

## Extensions

Some extensions implement alternative interpretations of the repository content. They
register a `requirement` to ensure that all users of the repository will be aware of the
special semantics.

For finding, installing and enabling extensions see
[UsingExtensions](https://wiki.mercurial-scm.org/UsingExtensions).

### Largefiles

The [largefiles](https://wiki.mercurial-scm.org/LargefilesExtension) extension is a part
of Mercurial. It puts special semantics into files in the `.hglf` directory and assumes
and ensure they are hashes of actual files. The actual files are fetched and pushed on
demand using special protocol commands.
