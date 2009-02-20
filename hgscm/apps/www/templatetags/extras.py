from django import template
from django.conf import settings
import random, os

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

def do_mercurial_tricks (parser, token):
    return MercurialTricksNode()

register.tag('mercurial_tricks', do_mercurial_tricks)
