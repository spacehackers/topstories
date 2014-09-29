import os
import redis
from flask import Flask, render_template, redirect, jsonify
from json import loads
from util import json, jsonp, requires_auth

app = Flask(__name__)
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

app = Flask(__name__)

@app.route('/admin')
@requires_auth
def admin():
    return 'Hello Admin!'

@app.route('/')
@json
@jsonp
def topstories():
    topstories = loads(r_server.get('topstories'))
    return topstories, 200

if __name__ == '__main__':
    app.debug = True
    app.run()
