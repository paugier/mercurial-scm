"""Reading, purging and gathering the style sheets."""

from __future__ import annotations

import posixpath
import re

from collections.abc import Callable, Iterable

import tinycss2

# path of the style sheet gathering all the others, from the root of the website
BUNDLE = "_static/site.css"

# at-rules containing rules
_GROUP_RULES = {"media", "supports", "layer", "container", "document"}

_WORD_RE = re.compile(r"[A-Za-z0-9_-]+")
_TAG_RE = re.compile(r"<([A-Za-z][A-Za-z0-9-]*)")
_CLASS_OR_ID_RE = re.compile(r"""\b(?:class|id)=["']([^"']*)["']""")
_NON_ASCII_RE = re.compile(r"[^\x00-\x7f]")
_EXTERNAL_RE = re.compile(r"^([a-z][a-z0-9+.-]*:|//|#)", re.IGNORECASE)


def is_external(url: str) -> bool:
    """Tell if a URL does not point to a file of the website.

    >>> is_external("https://example.org/a.css"), is_external("../a.css")
    (True, False)
    """
    return bool(_EXTERNAL_RE.match(url)) or url.startswith("/")


def html_names(html: str) -> set[str]:
    """Return the names of the elements, the classes and the ids of a page.

    >>> sorted(html_names('<div class="a b-c"><p id="d">class</p></div>'))
    ['a', 'b-c', 'd', 'div', 'p']
    """
    names = {tag.lower() for tag in _TAG_RE.findall(html)}
    for value in _CLASS_OR_ID_RE.findall(html):
        names.update(value.split())
    return names


def script_names(script: str) -> set[str]:
    """Return all the words of a script, any of them could be a class name.

    >>> sorted(script_names('element.classList.add("show", `fade-in`)'))
    ['add', 'classList', 'element', 'fade-in', 'show']
    """
    return set(_WORD_RE.findall(script))


class Purger:
    """Remove the rules of a style sheet which do not apply to any page.

    :param used: names of the elements, the classes and the ids of the pages
    :param safelist: patterns of names to consider as used
    :param font_face: called with the declarations of a `@font-face` rule and
        the path of the style sheet, returns the rule to write
    """

    def __init__(
        self,
        used: Iterable[str],
        safelist: Iterable[str] = (),
        font_face: Callable[[list, str], str] | None = None,
    ):
        self.used = set(used)
        self.safelist = [re.compile(pattern) for pattern in safelist]
        self.font_face = font_face
        # paths of the imported style sheets
        self.imported: list[str] = []
        self._known: dict[str, bool] = {}

    def is_used(self, name: str) -> bool:
        if name not in self._known:
            self._known[name] = name in self.used or any(
                pattern.search(name) for pattern in self.safelist
            )
        return self._known[name]

    def selector_is_used(self, tokens: list) -> bool:
        """Tell if a selector could match something.

        The attributes and the arguments of the pseudo-classes are not checked.
        """
        previous = None
        for token in tokens:
            if token.type == "ident":
                if previous == ".":
                    if not self.is_used(token.value):
                        return False
                elif previous != ":" and not self.is_used(token.value.lower()):
                    return False
            elif token.type == "hash" and not self.is_used(token.value):
                return False
            previous = token.value if token.type == "literal" else None
        return True

    def purge(self, css: str, path: str = "", read=None) -> str:
        """Return the used rules of a style sheet, without useless spaces.

        :param path: path of the style sheet, from the root of the website
        :param read: returns the content of an imported style sheet
        """
        rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
        return self._rules(rules, path, read)

    def _rules(self, rules: list, path: str, read) -> str:
        output = []
        for rule in rules:
            if rule.type == "qualified-rule":
                selectors = [
                    compact(selector)
                    for selector in split_list(rule.prelude)
                    if self.selector_is_used(selector)
                ]
                content = declarations(rule.content, path)
                if selectors and content:
                    output.append(f"{','.join(selectors)}{{{content}}}")
            elif rule.type == "at-rule":
                output.append(self._at_rule(rule, path, read))
        return "".join(output)

    def _at_rule(self, rule, path: str, read) -> str:
        keyword = rule.lower_at_keyword
        start = f"@{rule.at_keyword} {compact(rule.prelude)}".rstrip()
        if keyword == "charset":
            return ""
        if keyword == "import":
            url = next(
                (t.value for t in rule.prelude if t.type in ("url", "string")), None
            )
            if read is None or url is None or is_external(url):
                return f"{start};"
            imported = posixpath.normpath(posixpath.join(posixpath.dirname(path), url))
            self.imported.append(imported)
            return self.purge(read(imported), imported, read)
        if rule.content is None:
            return f"{start};"
        if keyword in _GROUP_RULES:
            rules = tinycss2.parse_rule_list(
                rule.content, skip_comments=True, skip_whitespace=True
            )
            content = self._rules(rules, path, read)
            if not content:
                return ""
            return f"{start}{{{content}}}"
        if keyword == "font-face" and self.font_face is not None:
            declarations = tinycss2.parse_blocks_contents(
                rule.content, skip_comments=True, skip_whitespace=True
            )
            return self.font_face(declarations, path)
        if keyword in ("font-face", "page"):
            content = declarations(rule.content, path)
        else:
            content = rebase_urls(compact(rule.content), path)
        return f"{start}{{{content}}}"


def split_list(tokens: list) -> list[list]:
    """Split the tokens of a list of selectors."""
    selectors = [[]]
    for token in tokens:
        if token.type == "literal" and token.value == ",":
            selectors.append([])
        else:
            selectors[-1].append(token)
    return selectors


def compact(tokens: list) -> str:
    """Serialize tokens with as few spaces as possible."""
    parts = []
    for token in tokens:
        if token.type == "comment":
            continue
        parts.append(" " if token.type == "whitespace" else token.serialize())
    return re.sub(r" +", " ", "".join(parts)).strip()


def declarations(content: list, path: str) -> str:
    """Serialize the content of a rule with as few spaces as possible."""
    items = tinycss2.parse_blocks_contents(
        content, skip_comments=True, skip_whitespace=True
    )
    if any(item.type != "declaration" for item in items):
        # something unusual, do not take any risk
        return rebase_urls(compact(content), path)
    return rebase_urls(";".join(declaration(item) for item in items), path)


def declaration(item) -> str:
    important = "!important" if item.important else ""
    return f"{item.name}:{compact(item.value)}{important}"


def rebase_urls(css: str, path: str) -> str:
    """Make the URLs relative to the style sheet gathering all the others."""

    def rebase(match: re.Match) -> str:
        url = match.group(2)
        if is_external(url):
            return match.group(0)
        return f'url("{relative_url(path, url)}")'

    if "url(" not in css:
        return css
    return re.sub(r"""url\(\s*(["']?)([^"')]+)\1\s*\)""", rebase, css)


def relative_url(path: str, url: str, base: str = BUNDLE) -> str:
    """Return the URL found in the file `path`, relatively to the file `base`.

    >>> relative_url("_static/vendor/css/all.css", "../fonts/solid.woff2?v=1")
    'vendor/fonts/solid.woff2?v=1'
    """
    url, separator, suffix = re.match(r"([^?#]*)([?#]?)(.*)", url).groups()
    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), url))
    relative = posixpath.relpath(target, posixpath.dirname(base))
    return relative + separator + suffix


def escape_non_ascii(css: str) -> tuple[str, set[int]]:
    """Escape the characters depending on the encoding of the style sheet.

    Return the style sheet and the code points of the escaped characters, which
    are the ones of the icons.

    >>> escape_non_ascii('a:before{content:"\\uf0c9"}')
    ('a:before{content:"\\\\f0c9 "}', {61641})
    """
    codepoints = set()

    def escape(match: re.Match) -> str:
        codepoint = ord(match.group(0))
        codepoints.add(codepoint)
        return f"\\{codepoint:x} "

    return _NON_ASCII_RE.sub(escape, css), codepoints
