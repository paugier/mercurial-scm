"""Tests of what makes incremental builds give the same website as clean ones."""

import json

from types import SimpleNamespace

from docutils import nodes
from sphinx import addnodes

from incremental_build import (
    STATE,
    IncrementalBuild,
    digest,
    load_state,
    navigation,
    posts,
    removed,
    static_files,
)


def toc(*entries, **attributes):
    toctree = addnodes.toctree(
        entries=[(None, entry) for entry in entries], **attributes
    )
    return nodes.bullet_list("", toctree)


def environment(**titles):
    return SimpleNamespace(
        titles={name: nodes.title(text=title) for name, title in titles.items()},
        tocs={name: toc("about") if name == "index" else toc() for name in titles},
    )


def test_navigation_changes_with_titles():
    before = navigation(environment(index="Mercurial", about="About"))
    assert before == navigation(environment(about="About", index="Mercurial"))
    assert before != navigation(environment(index="Mercurial", about="About us"))
    assert before != navigation(
        environment(index="Mercurial", about="About", new="New")
    )


def test_navigation_changes_with_toctrees():
    env = environment(index="Mercurial", about="About")
    before = digest(navigation(env))
    env.tocs["index"] = toc("about", "install")
    assert digest(navigation(env)) != before
    env.tocs["index"] = toc("about", caption="More")
    assert digest(navigation(env)) != before
    env.tocs["index"] = toc("about")
    assert digest(navigation(env)) == before


def post(**info):
    content = nodes.section("", nodes.paragraph(text=info.pop("text", "text")))
    return {"doctree": content, "excerpt": [content], **info}


def test_posts_changes_with_what_other_pages_show():
    def env(**info):
        return SimpleNamespace(ablog_posts={"news/a": [post(**info)]})

    before = posts(env(title="A", tags=["sprint"]))
    assert before == posts(env(title="A", tags=["sprint"], text="other text"))
    assert before != posts(env(title="B", tags=["sprint"]))
    assert before != posts(env(title="A", tags=["sprint", "release"]))
    assert posts(SimpleNamespace()) == []


def test_static_files(tmp_path):
    theme, site = tmp_path / "theme", tmp_path / "site"
    (theme / "js").mkdir(parents=True)
    site.mkdir()
    (theme / "js" / "a.js").write_text("a")
    (theme / "logo.svg").write_text("theme")
    before = static_files([theme, site])
    assert sorted(before) == ["js/a.js", "logo.svg"]

    (site / "logo.svg").write_text("site")
    after = static_files([theme, site])
    assert after["js/a.js"] == before["js/a.js"]
    assert after["logo.svg"] != before["logo.svg"]


def test_removed():
    assert removed(["a", "b", "c"], ["c", "a", "d"]) == ["b"]
    assert removed({"a": 1, "b": 2}, {"a": 3}) == ["b"]
    assert removed([], ["a"]) == []


def test_load_state(tmp_path):
    assert load_state(tmp_path) == {}
    (tmp_path / STATE).write_text("not json")
    assert load_state(tmp_path) == {}
    (tmp_path / STATE).write_text(json.dumps(["not", "a", "state"]))
    assert load_state(tmp_path) == {}
    (tmp_path / STATE).write_text(json.dumps({"pages": ["index"]}))
    assert load_state(tmp_path) == {"pages": ["index"]}


def test_remove(tmp_path):
    build = IncrementalBuild(SimpleNamespace(outdir=tmp_path))
    (tmp_path / "news" / "tag").mkdir(parents=True)
    (tmp_path / "news" / "tag" / "old.html").write_text("")
    (tmp_path / "news" / "kept.html").write_text("")
    (tmp_path / "alone" / "deep").mkdir(parents=True)
    (tmp_path / "alone" / "deep" / "old.html").write_text("")

    assert build.remove(tmp_path / "news" / "tag" / "old.html")
    assert build.remove(tmp_path / "alone" / "deep" / "old.html")
    assert not build.remove(tmp_path / "missing.html")
    assert sorted(path.name for path in tmp_path.rglob("*")) == ["kept.html", "news"]
