"""Tests of the reduction of the size of the website."""

from site_optimize import (
    BUNDLE,
    FontFaces,
    Purger,
    attributes,
    escape_non_ascii,
    html_names,
    optimize_head,
    relative_url,
    script_names,
    set_image_sizes,
    style_sheets,
)


def purge(css, used, safelist=()):
    return Purger(used, safelist).purge(css)


def test_html_names():
    html = '<div class="a b-c"><p id="d">class="not-this"</p></div>'
    assert html_names(html) >= {"div", "p", "a", "b-c", "d"}


def test_script_names():
    names = script_names('element.classList.add("show", `fade-in`)')
    assert {"show", "fade-in"} <= names


def test_purge_unused_rules():
    css = ".used { color: red; } .unused { color: blue; } p.used, i { margin: 0 }"
    assert purge(css, {"used", "p"}) == ".used{color:red}p.used{margin:0}"


def test_purge_needs_all_the_names():
    css = "div.a .b > #c { color: red }"
    assert purge(css, {"div", "a", "b"}) == ""
    assert purge(css, {"div", "a", "b", "c"}) == "div.a .b > #c{color:red}"


def test_purge_keeps_what_is_not_checked():
    css = "a:not(.unused):hover::before, [data-x=y], :root, * { color: red }"
    assert purge(css, {"a"}) == (
        "a:not(.unused):hover::before,[data-x=y],:root,*{color:red}"
    )


def test_purge_safelist():
    css = ".bs-tooltip-auto { color: red } .bs-other { color: red }"
    assert purge(css, set(), [r"^bs-tooltip-"]) == ".bs-tooltip-auto{color:red}"


def test_purge_group_rules():
    css = """
    @media (min-width: 960px) { .used { color: red } .unused { color: blue } }
    @media print { .unused { color: blue } }
    @supports (display: grid) { @media print { .used { margin: 0 } } }
    """
    assert purge(css, {"used"}) == (
        "@media (min-width: 960px){.used{color:red}}"
        "@supports (display: grid){@media print{.used{margin:0}}}"
    )


def test_purge_keeps_other_at_rules():
    css = "@keyframes spin { from { opacity: 0 } to { opacity: 1 } }"
    assert purge(css, set()) == "@keyframes spin{from { opacity: 0 } to { opacity: 1 }}"


def test_purge_keeps_values():
    css = ".a { --x: 1px; margin: calc(1px + 2px) 0 !important; color: red; }"
    assert purge(css, {"a"}) == (
        ".a{--x:1px;margin:calc(1px + 2px) 0!important;color:red}"
    )


def test_purge_imports():
    sheets = {"_static/basic.css": ".used { color: red } .unused { color: blue }"}
    purger = Purger({"used"})
    css = '@import "../basic.css"; .used { margin: 0 }'
    purged = purger.purge(css, "_static/styles/theme.css", sheets.__getitem__)
    assert purged == ".used{color:red}.used{margin:0}"
    assert purger.imported == ["_static/basic.css"]


def test_purge_rebases_urls():
    purger = Purger({"a"})
    css = ".a { background: url(../img/a.png), url('data:image/png;base64,AAA=') }"
    assert purger.purge(css, "_static/styles/theme.css") == (
        '.a{background:url("img/a.png"), url("data:image/png;base64,AAA=")}'
    )


def test_relative_url():
    assert relative_url("_static/a/b/c.css", "../d.woff2?v=1") == "a/d.woff2?v=1"
    assert BUNDLE == "_static/site.css"


def test_escape_non_ascii():
    css, codepoints = escape_non_ascii('a:before{content:""}')
    assert css == 'a:before{content:"\\f0c9 "}'
    assert codepoints == {0xF0C9}


def test_font_faces():
    css = """
    @font-face {
        font-family: "Icons";
        src: url(../webfonts/icons.woff2) format("woff2"),
             url(../webfonts/icons.ttf) format("truetype");
    }
    @font-face { font-family: "Text"; src: url(text.woff2) format("woff2") }
    """
    font_faces = FontFaces([r"/icons\."])
    purged = Purger(set(), font_face=font_faces).purge(css, "_static/vendor/css/a.css")
    assert list(font_faces.fonts) == ["_static/vendor/webfonts/icons.woff2"]
    assert "icons.ttf" not in purged
    assert purged.endswith(
        '@font-face{font-family:"Text";src:url("vendor/css/text.woff2") format("woff2")}'
    )


def test_attributes():
    tag = '<link rel="preload" crossorigin href="a.css?v=1" />'
    assert attributes(tag) == {"rel": "preload", "crossorigin": "", "href": "a.css?v=1"}


HEAD = """<html>
  <head>
    <link href="../_static/styles/theme.css?digest=1" rel="stylesheet" />
    <link href="../_static/vendor/fontawesome/6.5.2/css/all.min.css" rel="stylesheet" />
    <link rel="preload" as="font" type="font/woff2" crossorigin href="../_static/a.woff2" />
    <link rel="stylesheet" type="text/css" href="../_static/hg-custom.css?v=2" />
    <link rel="stylesheet" href="https://example.org/other.css" />
    <link rel="preload" as="script" href="../_static/scripts/bootstrap.js" />
    <script src="../_static/vendor/fontawesome/6.5.2/js/all.min.js?digest=1"></script>
    <script src="../_static/documentation_options.js?v=3"></script>
    <script src="../_static/doctools.js?v=4"></script>
    <script>DOCUMENTATION_OPTIONS.pagename = 'help/index';</script>
    <script defer="defer" src="https://example.org/other.js"></script>
    <link rel="icon" href="../_static/logo-droplets.svg"/>
  </head>
  <body>
    <link rel="stylesheet" href="../_static/ablog/tagcloud.css" />
    <script src="../_static/scripts/bootstrap.js"></script>
  </body>
</html>
"""

BUNDLED = [
    "_static/styles/theme.css",
    "_static/vendor/fontawesome/6.5.2/css/all.min.css",
    "_static/hg-custom.css",
]


def is_removed(path):
    return path.startswith("_static/vendor/")


def test_style_sheets():
    assert style_sheets(HEAD, "help/index.html") == BUNDLED


def test_optimize_head():
    optimized = optimize_head(HEAD, "help/index.html", BUNDLED, "abc123", is_removed)
    assert (
        optimized
        == """<html>
  <head>
    <link rel="stylesheet" type="text/css" href="../_static/site.css?v=abc123" />
    <link rel="stylesheet" href="https://example.org/other.css" />
    <link rel="preload" as="script" href="../_static/scripts/bootstrap.js" />
    <script src="../_static/documentation_options.js?v=3"></script>
    <script defer src="../_static/doctools.js?v=4"></script>
    <script>DOCUMENTATION_OPTIONS.pagename = 'help/index';</script>
    <script defer="defer" src="https://example.org/other.js"></script>
    <link rel="icon" href="../_static/logo-droplets.svg"/>
  </head>
  <body>
    <link rel="stylesheet" href="../_static/ablog/tagcloud.css" />
    <script src="../_static/scripts/bootstrap.js"></script>
  </body>
</html>
"""
    )


def test_optimize_head_again():
    """The pages which are not written again get the new style sheet."""
    optimized = optimize_head(HEAD, "help/index.html", BUNDLED, "abc123", is_removed)
    assert style_sheets(optimized, "help/index.html") == []
    assert optimize_head(optimized, "help/index.html", BUNDLED, "abc123") == optimized
    updated = optimize_head(optimized, "help/index.html", BUNDLED, "def456")
    assert updated == optimized.replace("abc123", "def456")


def test_set_image_sizes():
    sizes = {"_static/logo.svg": (100, 120), "_images/a.jpg": (800, 600)}
    html = (
        '<img src="../_static/logo.svg" alt="logo"/>'
        '<img alt="a" src="../_images/a.jpg" />'
        '<img alt="b" src="../_images/a.jpg" style="width: 150px;">'
        '<img alt="c" src="../_images/unknown.jpg" width="10" />'
        '<img src="https://example.org/d.png" />'
    )
    optimized = set_image_sizes(html, "news/post.html", sizes.get)
    assert optimized == (
        '<img src="../_static/logo.svg" alt="logo" width="100" height="120" />'
        '<img alt="a" src="../_images/a.jpg" width="800" height="600" />'
        '<img alt="b" src="../_images/a.jpg" style="width: 150px;"'
        ' width="800" height="600" loading="lazy" decoding="async">'
        '<img alt="c" src="../_images/unknown.jpg" width="10"'
        ' loading="lazy" decoding="async" />'
        '<img src="https://example.org/d.png" />'
    )
    assert set_image_sizes(optimized, "news/post.html", sizes.get) == optimized
