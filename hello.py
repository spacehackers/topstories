import os
import redis
from flask import Flask, render_template, redirect
from util import json, jsonp
from json import loads

app = Flask(__name__)
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == '__main__':
    app.debug = False
    app.run()
