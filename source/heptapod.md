---
sd_hide_title: true
---

# Heptapod

# Contributing to Mercurial through Heptapod

This document summarizes the contribution and review process for contributing to
Mercurial using Heptapod.

[Heptapod](https://heptapod.net/) is a friendly fork of GitLab Community Edition that
also supports Mercurial. [https://foss.heptapod.net](https://foss.heptapod.net) is a
public instance for Free and Open-Source Software (more information
[here](https://foss.heptapod.net/heptapod/foss.heptapod.net)).

```{note}
We recommend you start with the
[Quickstart Guide from Heptapod itself](https://heptapod.net/pages/quick-start-guide.html)
```

______________________________________________________________________

## 1. For Contributors

This section will present the workflow from a contributor's perspective.

### 1.1. Building Your Changes

Each contribution should be made in a series of small and independent patches, see
https://www.mercurial-scm.org/wiki/ContributingChanges.

That series of changesets **must** be part of a `topic`, a form of lightweight branching
provided by the `topic` extension.

We strongly recommend you enable the `evolve` extension too from the same Python package.
This is covered by
[Heptapod's Quickstart Guide](https://heptapod.net/pages/quick-start-guide.html)

### 1.2. Joining the Project on Heptapod

You need to create an account on foss.heptapod.net and request `Developer` access to
[the project](https://foss.heptapod.net/mercurial/mercurial-devel) by clicking the link
just under the logo, it should be granted to you very quickly.

People from Octobus have plans to improve the drive-by contribution experience to remove
this step, but the development effort required is non-trivial.

### 1.3. Sharing and testing your changes

While developing your changes, you can push them to Heptapod to test a full CI run[^1] or
get early feedback from specific people pre-review.

When you push to Heptapod, you will be offered a link to create a Merge Request (MR) in
the CLI. Follow that link to create a MR. Don't worry, you can also create the MR later
through the web UI.

````{note}
You can skip the CI if you don't need it yet and want to be a nice neighbor with
```sh
hg push -r REV --pushvars ci.skip=
```
````

You can create a MR early in the development process to make it easier to follow (for
example, to have a unique URL to check the results of CI runs), however please mark your
MR as "Draft" until it is ready for review. This is done using the pre-built button in
GitLab.

### 1.4. Submitting your change for review

When your changes are ready for review, simply take the following actions:

- Mark it as "Ready" (there is a button for that at the top of the MR). This is the
  default when opening an MR, but may be necessary after reviewer feedback

- Assign the `reviewer` field to the "Mercurial Review" user if not already the case

The change will then be picked up by reviewers who will provide feedback and eventually
accept it.

### 1.5. Discussing and applying feedback

If some aspect of your patches needs to be clarified or changed, reviewers will:

- Ask questions and request changes to your patches through comments

- Set the MR to "Draft" if it really is not ready for review

When this happens you should apply the feedback and answer the questions using the
comment system. Please make sure you use the threading system for clarity.

Do not mark the thread as resolved, that's the reviewer's responsibility.

Once all feedback and questions have been answered, you should leave a comment directed
at whoever asked for changes/questions.

### 1.6. When your series is accepted

In the general case, your series will eventually be accepted and become part of the main
history.

You don't need to do anything, the changesets will get published (in the Mercurial
sense), the topic will fade away and the MR will be automatically detected as "merged".
If the changesets needed a rebase or some small adjustment, changeset evolution will keep
track of that for you and a simple `hg evolve` after pulling should be enough.

### 1.7. Getting a series out of the review queue

If a series needs to be stashed away or if lengthy rework is expected, it is useful to
get it out of the review queue. To do so, mark it as "Draft".

### 1.8. Fully abandoning a series

If you want to fully abandon a series, keep track of your topic parent (usually `s0` in
`hg stack`), then simply use `hg prune -r topic(mytopic)` and push the (former) parent of
that topic `hg push --rev TOPIC_PARENT` to remove them from the server. (Pro-tip: any
descendant of the topic parent will work)

______________________________________________________________________

## 2. For reviewers

This section will present the workflow from a reviewer's perspective.

```{important}
For email patches, you will need to send a merge request with the emailed
patch series to wait for the CI to complete and merge the change. You do not need to add
"Mercurial Review" to reviewers, this is only a special case to ensure that pre-landing
CI is done for email patches.
```

### 2.1. Setup

First set up yourself to
[contribute through Heptapod](https://heptapod.net/pages/quick-start-guide.html).

Second, add this to your configuration. **This is very important to prevent you to
publish content by mistake**. People from Octobus are working on making this a
server-side check soon, for now this is the best we've got.

```ini
[experimental]
auto-publish = abort
```

### 2.2. Checking for series that need review

These are all non-"Draft" series with "Mercurial Review" as a reviewer.

Here's a bookmark:
https://foss.heptapod.net/mercurial/mercurial-devel/-/merge_requests?scope=all&state=opened&reviewer_username=mercurial.review&draft=no

### 2.3. Providing feedback on a review

If a series needs changes or clarification:

- Comment to provide feedback and use threads as much as possible

- Use the "request changes" option when submitting your feedback

- Set the series to "Draft" if it is \*really\* not ready for review

As a general rule, comments about a specific changeset should go on its diff, and
comments about the whole series should go to the general discussion page.

The reviewer (you), is responsible for marking thread as **resolved**. This will be made
easy to remember because merging is disallowed through the Web UI when conversations are
not resolved.

### 2.4. Approving a Series

There is an `Approve` button on MR, click it and your approval will be visible in the UI.
This is useful for users that don't have merge rights or simply to signify "Looks good,
but I want someone else to also look at this".

### 2.5. "Merging" the change

```{note}
This is the GitLab's notion of merge which does *not* necessarily mean a
merge changeset. In our case, we will forbid merge changesets and only allow
fast-forward merging.
```

If a series is ready to be merged, click the `Merge` button.

Merging a series is only possible if the CI passed, discussion are resolved and the
changes are rebased on the current branch head.

If you want to partially merge a series, create a new topic with a new MR to do so. This
validates that the CI is happy about the change you are about to merge.

______________________________________________________________________

## 3. References

### 3.1. Series States

Here is a summary of the states a series can be in.

| Reviewer is "Mercurial Review" | Marked "Draft" | Has approvals | Status                                                            |
| ------------------------------ | -------------- | ------------- | ----------------------------------------------------------------- |
| ❌                             | *Any*          | *Any*         | Series is not part of the review queue and will not be considered |
| ✅                             | ✅             | ❌            | Series needs answers or rework from the author                    |
| ✅                             | ❌             | ❌            | Series is waiting for review                                      |
| ✅                             | ❌             | ✅            | Series has been pre-reviewed and needs a second review            |

______________________________________________________________________

## 4. Current issues

### 4.1. Per-commit thread

We cannot currently easily comment on the commit message. GitLab is actively working on
it. The effort can be tracked here: https://gitlab.com/gitlab-org/gitlab/-/issues/19691.

In the meantime, people can still quote commit messages in regular comments and use the
first line of the commit for example.

### 4.2. Stacked topics

- Merging a stacked topic currently also merges the underlying topics

- All changesets (and changes in the full diff) from the underlying topics are visible in
  the stacked MR when reviewing

- There is no obvious way of telling apart changes from the current topic and from the
  ones below

Work on improving these issues is underway from Octobus, but it takes time, so please
bear with us. Help is always appreciated.

______________________________________________________________________

## 5. External tooling

It is fairly easy to connect automation to GitLab, currently nothing of the sort (that
could work well with Mercurial) has been written, but if someone wants to enforce some of
our convention with a bot, please go ahead.

Example actions that could be useful to script:

- automatically put series that fail CI back to "Draft",

- automatically rebase and "merge" series with enough "approvals".

[^1]: Please note that we may change this automatic-CI-on-push policy in the future if the
    stress on the CI is too large, restricting it to Merge Requests only.
