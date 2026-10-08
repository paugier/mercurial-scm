# Using Mercurial Extensions

Expanding the basic functionality of Mercurial with optional extensions.

## Introduction

Mercurial is designed to offer a small, safe, and easy to use command set which is
powerful enough for most users. Advanced users of Mercurial can be aided with the use of
Mercurial extensions. Extensions allow the integration of powerful new features directly
into the Mercurial core.

```{important}
Features in extensions may not conform to Mercurial's usual standards for safety, reliability, and ease of use.
```

Built-in help on extensions is available with `hg help extensions`
([online version](./help/topics/extensions.rst)). To get help about an enabled extension,
run `hg help <extension-name>`. If an extension provides a command with the same name,
you can use `hg help --extension <extension-name>` to get help about the extension
specifically.

Note that Mercurial explicitly does **not** provide a *stable API* for extension
programmers, so it is up to their respective providers/maintainers to adapt them to
[API changes](https://wiki.mercurial-scm.org/ApiChanges).

## Enabling an extension

To enable the "foo" extension, either shipped with Mercurial or in the Python search
path, create an entry for it in your hgrc, like this:

```ini
[extensions]
foo =
```

```{tip}
You can use `hg config --edit` to open the user-level config file.
```

You may also specify the full path to an extension (which may be either a .py file or a
folder containing `__init__.py`):

```ini
[extensions]
myfeature = ~/.hgext/myfeature.py
```

To get an extension which is not shipped with Mercurial, just download it to any place in
your filesystem. In the example above it was downloaded to `~/.hgext/`.

## Disabling an extension

To explicitly disable an extension enabled in an hgrc of broader scope, prepend its path
with `!`:

```ini
[extensions]
# disabling extension bar residing in /path/to/extension/bar.py
bar = !/path/to/extension/bar.py
# ditto, but no path was supplied for extension baz
baz = !
```

## Configuring an extension

Extensions can often be configured further in an extension-specific section in the same
configuration file. Refer to `hg help <extension-name>` or `hg help -e <extension-name>`.

## Extensions bundled with Mercurial

These extensions are maintained by the Mercurial project and are distributed together
with Mercurial.

| Name                                               | Description                                                                                     |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [acl](./help/extensions/acl.rst)                   | Manage commit access to parts of a repo using control lists                                     |
| [blackbox](./help/extensions/blackbox.rst)         | Log events to .hg/blackbox.log for post-mortem debugging                                        |
| [bugzilla](./help/extensions/bugzilla.rst)         | Update Bugzilla entries when a bug id is referenced in a changeset                              |
| [censor](./help/extensions/censor.rst)             | Erase file content at a given revision                                                          |
| [churn](./help/extensions/churn.rst)               | Show change statistics for mercurial operations per author                                      |
| [clonebundles](./help/extensions/clonebundles.rst) | Advertise pre-generated bundles to seed clones                                                  |
| [closehead](./help/extensions/closehead.rst)       | Close arbitrary heads without checking them out first                                           |
| commitextras                                       | (Advanced) Adds a new flag extras to commit                                                     |
| [convert](./help/extensions/convert.rst)           | Convert repositories from other SCMs into Mercurial                                             |
| [eol](./help/extensions/eol.rst)                   | Translate line-ending characters between working copy and repository                            |
| [extdiff](./help/extensions/extdiff.rst)           | Compare changes using external programs                                                         |
| [factotum](./help/extensions/factotum.rst)         | HTTP authentication with factotum                                                               |
| [fastexport](./help/extensions/fastexport.rst)     | Export repositories as git fast-import stream                                                   |
| [fsmonitor](./help/extensions/fsmonitor.rst)       | Integrates the file-monitoring program watchman with Mercurial to produce faster status results |
| [githelp](./help/extensions/githelp.rst)           | Try translating Git commands to Mercurial commands                                              |
| [gpg](./help/extensions/gpg.rst)                   | Sign changesets and check signatures using GPG                                                  |
| [hgk](./help/extensions/hgk.rst)                   | Graphical repository and history browser based on gitk                                          |
| [highlight](./help/extensions/highlight.rst)       | Highlight syntax in the file revision view of hgweb                                             |
| [histedit](./help/extensions/histedit.rst)         | Edit, fold, drop changesets in the style of `git rebase --interactive`                          |
| [keyword](./help/extensions/keyword.rst)           | Use CVS-like keyword expansion in tracked files                                                 |
| [largefiles](./help/extensions/largefiles.rst)     | Track large binary files (new in 2.0)                                                           |
| [mq](./help/extensions/mq.rst)                     | Mercurial Patch Queues - manage changes as series of patches                                    |
| [notify](./help/extensions/notify.rst)             | Send email to subscribed addresses to notify of repository changes                              |
| [patchbomb](./help/extensions/patchbomb.rst)       | Send a collection of changesets as a series of patch emails                                     |
| [rebase](./help/extensions/rebase.rst)             | Move revisions from one part of history onto another                                            |
| [relink](./help/extensions/relink.rst)             | Recreate hardlinks between repository clones                                                    |
| [schemes](./help/extensions/schemes.rst)           | Add shortcuts to URLs as URL schemes                                                            |
| [share](./help/extensions/share.rst)               | Share repository history between several working directories                                    |
| [transplant](./help/extensions/transplant.rst)     | Cherry-pick, rebase and rewrite changesets                                                      |
| [win32mbcs](./help/extensions/win32mbcs.rst)       | Allow to use shift_jis/big5 filenames on Windows                                                |
| [zeroconf](./help/extensions/zeroconf.rst)         | Announce and browse repositories via Zeroconf/Bonjour                                           |
