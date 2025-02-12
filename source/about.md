---
sd_hide_title: true
---

# About

# Mercurial source control management

**Mercurial is a free, distributed source control management tool. It offers you the
power to efficiently handle projects of any size while using an intuitive interface. It
is easy to use and hard to break, making it ideal for anyone working with versioned
files.**

## Distributed architecture

Traditional version control systems such as Subversion use typical client-server
architectures with a central server to store the revisions of a project. In contrast,
Mercurial is truly distributed, giving each developer a local copy of the entire
development history, working independently of network access or a central server.
Committing, branching and merging are fast and cheap.

## Fast

Mercurial's implementation and data structures are designed to be fast. You can generate
diffs between revisions, or jump back in time within seconds. Therefore Mercurial is
perfectly suitable for large projects such as Firefox (https://hg.mozilla.org/) or
[Heptapod] (a GitLab fork supporting Mercurial,
[hg repositories](https://foss.heptapod.net/heptapod/)).

## Platform independent

Mercurial was written with platform independence in mind, and so most of Mercurial is
written in Python, with a small part in portable C for performance reasons. As a result,
binary releases are available on all major platforms. We also have a growing part that is
written in Rust - although it only currently officially supports Linux - binary releases
for which are coming very soon.

## Extensible

The functionality of Mercurial can be increased with extensions, either by activating the
official ones which are shipped with Mercurial, downloading some
[from the wiki](https://www.mercurial-scm.org/wiki/UsingExtensions) or by
[writing your own](https://www.mercurial-scm.org/wiki/WritingExtensions). Extensions are
written in Python and can change the workings of the basic commands, add new commands and
access all the core functionality of Mercurial.

## Easy to use

Mercurial sports a consistent command set, in which most Subversion users feel right at
home. Potentially dangerous actions are available via extensions you need to enable, so
the basic interface is easy to use, easy to learn and hard to break. The
[Quick Start](./quickstart.md) should get you going in a just few minutes.

## Open source

Mercurial is free software licensed under the terms of the
[GNU General Public License Version 2](http://www.gnu.org/licenses/gpl-2.0.txt) or any
later version.

## Similar projects

Mercurial is used for version control of files. Similar projects include [Git], [Pijul]
or [Jujutsu]. Version control systems without a distributed architecture include
[Subversion] and [CVS].

## This website

This website is a project of the Mercurial community. The source is licensed under GPLv2
or later. Feel free to send us patches.

[cvs]: https://www.nongnu.org/cvs/
[git]: https://git-scm.com/
[heptapod]: https://heptapod.net/
[jujutsu]: https://github.com/jj-vcs/jj
[pijul]: https://pijul.org/
[subversion]: https://subversion.apache.org/
