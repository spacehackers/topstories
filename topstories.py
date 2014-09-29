import os
import redis
import requests
import feedparser
import datetime
import dateutil.parser
from json import loads, dumps

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

    # keep track of when we add a new top story
    new_top_stories = {}

    for url in news_feeds:
        feed = feedparser.parse(url)
        for post in feed.entries:

            # nowsearch each term against each post.title
            for probe_name, terms in search_terms.items():
                for term in terms:

                    if post.title.find(term) > -1:

                        # use feedparser's published_parsed to find the published date as time.struct_time
                        # convert it to a string and that's what gets stored in redis
                        # and convert it to a datetime.datetime object for comparing to other post dates
                        published_str = datetime.datetime(*post.published_parsed[:6]).isoformat()
                        published = dateutil.parser.parse(published_str)

                        if probe_name in topstories:

                            # we already have post for this probe
                            # only replace it if this date is more recent
                            if published != max([published, dateutil.parser.parse(topstories[probe_name]['published_str'])]):
                                continue  # the one we already have is the latest, move along
                            else:
                                new_top_stories.setdefault(probe_name, []).append({'title':post.title, 'link':post.link, 'published_str': published_str})

                        # add it for first time
                        try:
                            topstories[probe_name] = {'title':post.title, 'link':post.link, 'published_str': published_str, }
                        except AttributeError:
                            if __name__ != "__main__":
                                print "can't find a post.title, post.link, here is post:"
                                print post

    r_server.set('topstories', dumps(topstories))

    if new_top_stories:
        # send an email digest!
        pass

    return topstories

if __name__ == "__main__":
    topstories = update_topstories()
    for n, p in topstories.items():
        print "%s:" % n
        print p
        print '==='
