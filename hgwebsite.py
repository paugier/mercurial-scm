#
# (c) 2014 David Soria Parra <dsp@php.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
import os
import flask

app = flask.Flask(__name__)


@app.route('/')
def indexpage():
    return flask.render_template('frontpage.html')


@app.route('/<site>')
def about(site=None):
    if not site:
        flask.abort(404)
    tpath = os.path.join('templates', site, 'index.html')
    if not os.path.exists(tpath):
        flask.abort(404)
    t = os.path.join(site, 'index.html')
    return flask.render_template(t)


if os.getenv("HGWEBSITE_DEBUG", None):
    app.debug = True

if __name__ == '__main__':
    app.run()
