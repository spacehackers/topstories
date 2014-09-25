import os
import redis
from flask import Flask, render_template, redirect
import feedparser
import requests
from topstories import fetch_news

app = Flask(__name__)
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

app = Flask(__name__)

@app.route('/')
def news():
    news = fetch_news()
    return flask.jsonify(**news)  # may timeut.. todo: move to redis + scheduler


if __name__ == '__main__':
    app.debug = False
    app.run()
