---
# uncomment the date to publish
# date: "2025-01-31"
category: project
tags: [internship]
---

# Towards native Github support for Mercurial

Git/Github and Gitlab are so central nowadays in programming that any new versioning tool has
to be highly compatible with Git. The two recent projects [Sapling] and [Jujutsu] (also
called `jj`) are both "Git compatible".

- Sapling website says that it "integrate[s] with Git":

  "Sapling client also supports cloning and interacting with Git repositories and can be
  used by individual developers to work with GitHub and other Git hosting services."

- Jujutsu describes itself as "A Git-compatible VCS that is both simple and powerful":

  "Today, we use Git repositories as a storage layer to serve and track content, making
  it compatible with many of your favorite Git-based tools, right now! All core
  developers use Jujutsu to develop Jujutsu, right here on GitHub."

The situation is not as good for Mercurial. There are currently two extensions to
interact with a Git repo:

- the core extension
  [hgext.git](https://foss.heptapod.net/mercurial/mercurial-devel/-/tree/branch/default/hgext/git)
  ("core" means provided with the Mercurial package).

  For this extension, one needs to clone, pull and push using `git`. Mercurial interacts
  with the local Git repo using [pygit2]. Changes have recently been done in `hgext.git`.
  However, it is still not compatible with recent version of [pygit2] and very limited,
  for example `hg st` is not implemented!

- the external extension [hg-git](https://foss.heptapod.net/mercurial/hg-git).

  I use [hg-git] for all my interactions with Git repos and it works well.

  In this case, Mercurial maintains with [Dulwich] a Git repo in the directory `.hg`.
  Therefore, hg-git works with two local repositories (one in Mercurial and another in
  Git), which is clearly not optimal in terms of memory and performance (especially for
  cloning). The other main limitation of hg-git is that it is not compatible with modern
  Mercurial using the topic and evolve extension. Git branches are represented with
  Mercurial bookmarks. These are indeed the closest equivalent to Git branches but the
  user experience is much less nice than with Mercurial topics, which is the modern
  Mercurial object to represent "feature branches".

  Another issue with hg-git is that the result of the conversion obtained after a pull is
  not stable, which highly limits the possibility that several people collaborate on the
  Mercurial side. However, this could change with the upcoming hg-git 1.2.

Therefore, there is nowadays no perfect solutions to interact with a remote Git
repository with modern Mercurial. However, another better strategy could be used.
Mercurial could consume and create on-the-fly the main data structure used by Git
(packfiles). This could be quite efficient and could be to some extend compatible with
modern Mercurial. We need to build a proof of concept to better evaluate this possible
solution. It could be done during an internship.

[dulwich]: https://pypi.org/project/dulwich
[hg-git]: https://wiki.mercurial-scm.org/HgGit
[jujutsu]: https://github.com/jj-vcs/jj
[pygit2]: https://pypi.org/project/pygit2/
[sapling]: https://sapling-scm.com/
