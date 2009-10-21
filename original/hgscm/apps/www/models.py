from django.db import models
from django.utils import simplejson
from django.conf import settings
import os, re

def get_download(platform, version):
    '''get the download for the right version'''
    f = open(os.path.join(settings.MEDIA_ROOT, "downloads.json"))
    list = simplejson.load(f)
    f.close()
    latest = version == 'latest' or not version
    for entry in list:
        if (latest and entry['latest'] == 'true') or entry['version'] == version:
            for version in entry['versions']:
                if version['identifier'] == platform:
                    return version
def get_download_for_agent(agent, version):
    '''get the download for the right version'''
    f = open(os.path.join(settings.MEDIA_ROOT, "downloads.json"))
    list = simplejson.load(f)
    f.close()
    latest = version == 'latest' or not version
    for entry in list:
        if (latest and entry['latest'] == 'true') or entry['version'] == version:
            for version in entry['versions']:
                if re.search(version['system'], agent):
                    return version

def get_latest_version():
    '''return the latest available version'''
    f = open(os.path.join(settings.MEDIA_ROOT, "downloads.json"))
    list = simplejson.load(f)
    f.close()
    for entry in list:
        if entry['latest'] == 'true':
            return entry['version']
