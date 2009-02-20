from django import template
from django.conf import settings
from django.template import Context
from hgscm.apps.www.models import get_latest_version, get_download_for_agent, get_download
import random, os, re

register = template.Library()

class MercurialTricksNode(template.Node):
    def __init__(self):
        self._filename = self._random()

    def _random(self):
	file = random.choice(os.listdir(settings.MERCURIAL_TRICKS))
        return os.path.join(settings.MERCURIAL_TRICKS, file)

    def render(self, context):
        f = open(self._filename)
        result = "<p><h3>Tricks</h3>" + f.read() + "</p>"
        f.close()
        return result

class DownloadButtonNode(template.Node):
    def __init__(self, extended):
        self._extended = extended
    def render(self, context):
        agent = context['request'].META['HTTP_USER_AGENT']
        t = template.loader.get_template('fragments/downloadbutton.html')
        c = Context()

        version = get_download_for_agent(agent, 'latest')
        if not version:
            version = get_download('source', 'latest')
        c['download_system'] = version['system']
        c['download_url'] = version['url']
        c['latest_version'] = get_latest_version()
        c['extended'] = self._extended
        return t.render(c)

def do_mercurial_tricks (parser, token):
    return MercurialTricksNode()

def do_download_button(parser, token):
    extended = len(token.split_contents()) > 1
    return DownloadButtonNode(extended)

register.tag('mercurial_tricks', do_mercurial_tricks)
register.tag('download_button', do_download_button)
