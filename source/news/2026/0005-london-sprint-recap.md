---
date: '2026-06-01'
category: communication
tags: [sprint]
---

# Recapping the London sprint

The sprint is already over!

The sprint was set in motion and organized by Pierre-Yves David and Raphaël
Gomès, both maintainers of Mercurial working at [Octobus](https://octobus.net/).

# XXX should we also shout out to Arun, 

Thanks to the gracious hosting by [Jane Street](https://www.janestreet.com), we
gathered a bit less than 20 people every day and managed to discuss and work on
a large variety of subjects, including truly riveting discussions over the
genetics of cross-breeding apples and oranges over lunch break.

We were too busy during the sprint to remember to take a picture of everyone, so
we unfortunately only have a few pictures of whiteboards, as pictured:

![A picture of a whiteboard with a lot of drawing relating to FUSE][0]

# XXX Maybe one or 1 photo of London to illustra the article, the white board picture is a bit obscure (can be integrated later on)

# like https://commons.wikimedia.org/wiki/London#/media/File:London_Skyline_(125508655).jpeg
# https://commons.wikimedia.org/wiki/File:City_of_London_skyline_from_London_City_Hall_-_Oct_2008_-_Aligned.jpg
# https://commons.wikimedia.org/wiki/File:Tower_Bridge_view_at_dawn_crop.jpg

## Day 1 - Wednesday 27th

The first day saw everyone get started on tasks that they either had wanted to
get done for a long time, or that sparked up from ad-hoc discussions.

XXX low level opinion that it could be clearer?
This was very much the point of this first day: a focus on boostrapping
occasional contributor and overall project maintenance.

If we include everything submitted during the 3-day window as far as visible
changes go, we received a few bug fixes ([#1965][1], [#1968][2], [#1969][3],
[#1970][4], [#1971][5], [#1976][6]), some documentation ([#1967][7], [#1975][8],
[poulpe#82][9]) and website improvements ([hg-website#31][10]), a new debug
command ([#1973][11]) to create a synthetic repo from a DAG,

# XXX the topic for the command to create synthetic repo from a DAG is still at super early stage and basic. I would probably not include it.

and some good
progress on larger work that never gets enough attention ([#1974][12],
[#1966][13]). We also hatched a plan with Matt Harbison remoting in from the US
to fix the Windows console encoding deprecation problem.

Progress was made on projects external to Mercurial but very much integral to
its ecosystem. Manuel Jacob helped lay out a plan for [hg-git's][14] tech debt,
while Georges Racinet handled Heptapod's [18.10.4][15] and [18.11.4][16]
releases, while working towards making Heptapod "cloud native" by GitLab's
definition ([heptapod#1647][17]).

Finally, for people who weren't busy with the above or getting familiar with new
features of Mercurial, it was time to already start more high-level discussions.
These discussions kept going for most of the rest of the sprint... which brings
us to day 2 and 3!

## Day 2 and 3 - Thursday 28th and Friday 29th

The agenda for days 2 and 3 was to get everyone familiar with the latest,
current and future developments of Mercurial, as well as to discuss concepts
from the larger VCS ecosystem. Here are some of the larger discussions we can
remember.

### A Virtual File System for Mercurial

As repositories grow larger and larger, filesystem overhead gets to be more and
more noticeable, both in terms of disk usage and speed. Even a fast Rust
parallel implementation of `hg update` can take up to several seconds for large
working copies, with kernel writes and inode creation overhead at the center of
the slowdown.

It's no secret that tech giants like Microsoft or Meta have used virtual file
systems to fight this scale and improve their developer experience, and it's
time for Mercurial to grow its FOSS, fully integrated VFS.

Upstream development of this effort was started earlier this year. The first
experimental read-only and local version based on fuse is already being used by real users in
conjunction with an overlay filesystem to support writes.
This has improved the
time to first interaction for a new working copy in the worst cases from 20s+ to
under 2s, with only a 10-20% overhead in normal operations.

During the sprint, the discussions were mostly about planning what's next for the
VFS: faster update still, seamless support in `hg status` and `hg update`,
and an integrated
write layer.

### Heptapod, our friendly GitLab fork

[Heptapod](https://heptapod.net) is a major way that Mercurial stays relevant
both for the FOSS community and professional users. Its maintainer Georges
Racinet gave a small presentation about its current state and its future, right
after being done keeping up with the latest GitLab releases.

This discussion helped clear a few misconceptions about Heptapod, fix a couple
of small user problems as well as helped with the `hg-git` effort. Finally, some
of the blockers for upgrading Heptapod to Mercurial 7.2 have been identified and
will be dealt with soon.

### Scaling obsmarker exchange and bundle caching

Florian Horn, Laurent Bulteau and Pierre-Yves David presented and discussed with
other attendees new developments that are currently being upstreamed. We have an
upcoming set of algorithms and formats that enable significant performance and
storage improvements for both exchanging obsolescence markers and improve the
cache of bundles.

While the mathematical modelling has been underway for a long time, we have
finally been able to start the upstream implementation and we will most likely
cover that whole topic in a separate post when it becomes usable.

### First-class conflicts

As soon as you can do multiple things concurrently, you will have conflicts: they are
an inevitable part of version control and many version control systems give you
neither a good model nor a good interface to help you with them.

[Pijul](https://pijul.org) (the spiritual successor to
[Darcs](https://darcs.net)) is the only active version control system that we
know of with a mathematical model of conflicts.

# XXX a bit fuzzy, maybe we should talk about CRDT more directly?
# XXX
# XXX A key point discussed at the print is that "A conflict is an ambiguity", we could cite that, (but maybe later)

For our users, this model can be thought of as an extension of the Mercurial
branching model: multiple heads on a branch is a natural consequence of things
happening at the same time in a distributed branching model, conflicts are the
natural consequence of things happening at the same time in a distributed
version control system.

Why should we model file changes any differently than we do branches? It turns
out that this model's contact with the real world is not without its share of
headaches, and there are still a lot of things to iron out. Pierre-Étienne
Meunier, creator and maintainer of Pijul, has been very open to collaboration
# XXX "and has helped us on these issues over the past few years."
# XXX in pratique, while we discuss from time to time, we lacked the time to properly collaborate, and not actual problem were worked one in theses paste years.

Of course, lately the [JJ](https://docs.jj-vcs.dev/latest) VCS has become very
popular, with its own flavor of first-class conflicts. Some users seem to
get a lot of mileage out of it and we can definitely learn something from the
use cases it covers. Nevertheless, a more general and complete model is needed
as there are edge cases were the approach suffer.
Conflict handling turns out to be especially painful in the context of
distributed safe mutable history, a central feature unique to Mercurial.

To that end, a lot of people gathered during the sprint to discuss how
first-class conflicts can be brought to Mercurial, as well as other tools like
Git or JJ. Caleb Owens from [GitButler](https://gitbutler.com) has already
written down some of his thoughts in [a small article][18]!

The discussions covered many topics.
How to formally defined some of core concept:
What's a change? What's a merge, What's a conflict?
What's the strength and weakness of each main model, merging state (git, hg,
jj) or merging patches (pijul).
What could it actually means to do a N way merge with multiple parents in the "state".
Why are history rewriting (and rebase in particular) and challenge for "patch" model.

While the couple of hour of discussion didn't magically produces perfect
solutions.
It helped the participants to share knowledge and get
a fresh angle on the problems.

# XXX probably drop this, but the replacement is not-equivalent
#
# Most of the discussion was spent looking at example cases, and re-inventing the
# Pijul model from first principles thanks to Florian and Laurent (who knew that
# different mathematicians could come up with the same ideas!). A hybrid world
# where immutable changes (the "public phase" in Mercurial) are still stored in a
# Merkle tree, but mutable changes (the "draft phase") are represented as real
# patches is still a goal we strive for. More work needs to happen, but we feel
# that it is possible.

### Normalized and composable history sharding

Back in 2018, Google upstreamed their `narrow` extension, which allows for
clones to fetch a subset of the history of files. It has been put to good use
but has always been quite brittle without Google's infrastructure and required a
lot of working around problems.

During the 7.2 cycle, we started implementing a new model for this
semi-centralized workflow: shapes. A shape is configured server-side, and is
used to define a set of paths to consider for clients of the narrow server. And
it does so through the entire history, regardless the state of these files in
the heads of the repository (deleted, for example).

Here the advantages of store shapes over the old system::

  * We can define clonebundles for usual patterns
  * We can nest and generally compose includes and excludes
  * We can generate a fingerprint for equivalent patterns
  * We can require that the server and the client agree on patterns
  * Client are made aware of changes on the server, invalidating their patterns
  * A solid permissions system could be built on top of store shapes
  * Some legacy problems (e.g. CLI parsing) will be solved

This sprint helped crystalize the concepts and possibilities for a few users,
some of whom seemed keen in sponsoring some of that work to benefit their
corporate usage.

### Evolution: safe mutable distributed history

Mercurial's Changeset Evolution concept have been around for a while and is the
corner stone of how Mercurial is capable of safe and simple collaboration on
draft history in a fully distributed setup.

At the sprint Caleb Owens presented how GitButler is approaching these collaboration problems.
How GitButler are trying to extend git data model to tracks more information to supports these usecases.

The current git data model creates some challenges, the model for storing
content is a CRDT, the branching model isn't so dealing with distributed change
affecting branches is complex.
This led Gitbutler to start with a rather centralised approach, with
constrained synchronisation phases.
These clear synchronisation barriers offer an opportunity to detect the
intrinsic issues of distributed history edit and provide a UX to solve them.
On the other hand, Mercurial data model, can a wider set of history editing
information while retaining its full CDRT property.
This can express a wider set of state without the need to solve theses issues
at synchronisation time.
While we believe the richer model of Mercurial allows to more flexible and
powerful workflow, the GitButler work on UX is quite interesting and each
approach have to learn from the other one.

Regarding user experience, we also discussed the downside of eagerly rebasing
changeset during history edition, and how some rebases are not properly
reversible, "silently" dropping some changes.

A wider roundtable of changeset evolution users let them express what they liked and disliked about the current experience in Mercurial.
Finally we discussed how to adapt GitLab's marge-bot[21] for Heptapod.
The result of this discussion has already been put in production.

### Git compatibility (embrace, extend, extinguish)

It is no secret that Git has won the popularity contest and currently sits at
the very top of general-purpose usage for version control. There has existed
tools to use [Git repos in Mercurial][19] and [vice versa][20] for a very long
time now, but none of them are supported in the core of either VCS.

Caleb Owens representing the Git world and Raphaël Gomès representing the
Mercurial world discussed the very real possibility of Mercurial becoming a
great Git server, building on top of the many projects currently underway. This
idea was floated around at the previous minisprint in Grenoble hosted by Pierre
Augier,
# XXX I would not throw Patrick under the bus here (pulling gitlab with him)
# XXX for something super hypothetical
# XXX
# XXX and has been a topic of discussion with Patrick Steinhardt for a few
# XXX months now.

In more concrete terms, Mercurial's scaling capabilities could soon allow it to
transparently speak Git's wire protocol and deliver unmatched performance for
clones and fetches.

# XXX it's not so much the scaling capability that are used to speak Git, but
# XXX more about speaking git that would give access to Mercurial scaling
# XXX capability to a wider audience.
# XXX
# XXX being able to translate things quickly is part of the equation, but just
# XXX a part of it. They key point is the improvement and extensibility of
# XXX Mercurial storage (and data model)

Separately, a Mercurial repository could easily expose a fake Git repository for
simple use cases (IDEs, shell prompt, AI agents, etc.) using a similar VFS approach than the one
detailed above.

Fixing the general problem of bi-directional Git support seems like it's not
worth the work, but supporting 90% of use cases could already make Mercurial
very relevant as a tool for the future of both client-side and server-side.

# XXX I feel like we are overselling the current plan as "coming soon". The
# XXX doesn't seems like a good idea.

### The Hyperlog, a new powerful storage format

The revlog is the underlying storage format of all user data, and has been since
the beginning of the project. After a brief revlog-v0 period of 1 year, version
1 of the revlog has been with us for more than 20 years now, scaling
(surprisingly?) well to 10s of millions of revisions and millions of files,
partly thanks to very significant but incremental improvements like
`generaldelta`, `zstd`, `sparserevlog`, and many runtime optimizations.

With all of this said, the format has been showing signs of weakness for a long
time and would be unable to truly usher us into the next jump in scale or user
experience. We have been working for a couple of years towards a new version of
the revlog: "v2". We nicknamed it `Hyperlog` for the purpose of convincing management.
And while that name started out as a joke, but it feels
perfectly corny and a worthy successor of `RevlogNG`, the original name of V1.

Here is a non-exhaustive list of features that were discussed at the sprint:
* Mutable index entries
* Multiple index and data blocks/files for extensibility and memory locality
* Sparse files with default values
* Better transactionality
* Unified filelogs, massively reducing the number of files on disk

There are huge scaling implications that come with this extensible of a format:
truly first-class changeset evolution, correct and fast narrowing and widening,
faster discovery, and generally many things that required a (usually brittle and
somewhat slow) cache will now be part of an index, without penalizing the main
index. This time, the format will also be sightly different for the changelog,
manifestlog and filelogs.

## Meta-recap

Overall, the sprint was a success!

We made a lot of progress in different areas, and had people from multiple companies
and projects highly involved the entire time, all within a fun atmosphere that
kept going well after business hours.

A few people were missing from last minute planning changes on their side, but
we are hoping to see them (and more!) in the next edition of the sprint, which
we are yet to start planning.

[0]: /_static/2026-london-sprint/whiteboard.jpg "A long discussion about FUSE"
[1]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1965
[2]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1968
[3]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1969
[4]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1970
[5]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1971
[6]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1976
[7]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1967
[8]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1975
[9]: https://foss.heptapod.net/octobus/poulpe/-/merge_requests/82
[10]: https://foss.heptapod.net/mercurial/hg-website/-/merge_requests/31
[11]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1973
[12]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1974
[13]: https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests/1966
[14]: https://foss.heptapod.net/mercurial/hg-git
[15]: https://foss.heptapod.net/heptapod/heptapod/-/work_items/2687
[16]: https://foss.heptapod.net/heptapod/heptapod/-/work_items/2690
[17]: https://foss.heptapod.net/heptapod/heptapod/-/work_items/1647
[18]: https://cto.je/tech/should-badmerge-conflict
[19]: https://hg-git.github.io
[20]: https://github.com/glandium/git-cinnabar
[21]: https://gitlab.com/marge-org/marge-bot
