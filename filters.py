import markdown as _markdown
from jinja2 import Markup

md = _markdown.Markdown(extensions=['toc'], safe_mode=False)

def mdown(value):
    return Markup(md.convert(value))
