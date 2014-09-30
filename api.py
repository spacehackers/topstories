import os
import redis
from flask import Flask, render_template, redirect, jsonify, url_for, abort
from json import loads, dumps
from util import json, jsonp, requires_auth
from topstories import get_search_terms_by_probe
from forms import SpaceProbeForm

app = Flask(__name__)
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

app = Flask(__name__)


@app.route('/')
@json
@jsonp
def topstories():
    topstories = loads(r_server.get('topstories'))
    return topstories, 200


@app.route('/<probe_name>')
@json
@jsonp
def topstories_single(probe_name):
    topstories = loads(r_server.get('topstories'))
    try:
        return topstories[probe_name], 200
    except KeyError:
        abort(404)


@app.route('/admin/<probe_name>/update.html', methods = ['POST'])
@requires_auth
def admin(probe_name):
    topstories = loads(r_server.get('topstories'))
    topstories_archive = loads(r_server.get('topstories_archive'))
    form = SpaceProbeForm(csrf_enabled=False)

    if form.validate_on_submit():
        # archive the old
        if form.probe_name.data in topstories:
            topstories_archive[form.probe_name.data] = topstories[form.probe_name.data]
        # update the new
        topstories[form.probe_name.data] = {'title':form.title.data, 'link':form.url.data, 'published': form.date.data }
        # save to redis
        r_server.set('topstories', dumps(topstories))
        r_server.set('topstories_archive', dumps(topstories))

        return redirect(url_for('admin_main', _anchor=form.probe_name.data))
    return 'fail'


@app.route('/admin/<probe_name>/')
@requires_auth
def admin_probe(probe_name):
    probe_name = ' '.join(probe_name.split('_'))
    topstories = loads(r_server.get('topstories'))
    try:
        post = topstories[probe_name]
    except KeyError:
        post = {}

    kwargs = {'probe_name': probe_name, 'post':post, 'form':SpaceProbeForm(csrf_enabled=False)}
    return render_template('admin_probe.html', **kwargs)


@app.route('/admin/')
def admin_main():
    spaceprobes = get_search_terms_by_probe()
    topstories = loads(r_server.get('topstories'))
    kwargs = {'topstories':topstories, 'spaceprobes': spaceprobes}
    return render_template('admin.html', **kwargs)


if __name__ == '__main__':
    app.debug = True
    app.run()
