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
