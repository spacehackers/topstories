import os
import redis
from json import loads, dumps
import requests
import feedparser

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

def update_topstories():
    """ fetches topstories from rss feeds and updates redis """

    try:
        topstories = loads(r_server.get('topstories'))
    except TypeError:
        topstories = {}

    # collect search terms from google doc
    search_terms_csv_url = 'https://docs.google.com/spreadsheet/pub?key=0AtHxCskz4p33dEs5elE0eUxfd3Z4VnlXTVliVWJxRHc&single=true&gid=4&output=csv'
    response = requests.get(search_terms_csv_url)
    assert response.status_code == 200, 'Wrong status code'

    search_terms = {}
    for line in response.content.split("\n"):
        probe_name = line.split(',')[0].replace(',',' ').strip()
        search_terms[probe_name.lower()] = [l for l in line.split(',')[1:] if l]  # removes empty strngs

    # read each feed
    with open('news_feeds.txt') as f:
        news_feeds = f.readlines()[1:]

    for url in news_feeds:
        feed = feedparser.parse(url)
        for post in feed.entries:

            # nowsearch each term against each post.title
            for probe_name, terms in search_terms.items():
                for term in terms:

                    if post.title.find(term) > -1:

                        if probe_name in topstories:
                            # we already have post for this probe
                            # only replace it if this date is more recent
                            if post.published_parsed != max([post.published_parsed, topstories[probe_name]['published_parsed']]):
                                continue

                        # add it for first time
                        try:
                            topstories[probe_name] = {'title':post.title, 'link':post.link, 'published_parsed': post.published_parsed, 'published': post.published}
                        except AttributeError:
                            if __name__ != "__main__":
                                print "can't find a post.title, post.link, or post.published, next is post:"
                                print post

    # remove the published_parsed before returning as they are not jsonify-able
    for probe_name, post in topstories.items():
        del topstories[probe_name]['published_parsed']

    r_server.set('topstories', dumps(topstories))

    return topstories

if __name__ == "__main__":
    topstories = update_topstories()
    for n, p in topstories.items():
        print "%s:" % n
        print p
        print '==='
