import os
import redis
import requests
import feedparser
import datetime
import dateutil.parser
from json import loads, dumps
from collections import OrderedDict
from util import send_email

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r_server = redis.StrictRedis.from_url(REDIS_URL)

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', None)

# if a headline includes these terms, skip it
exclude_terms = [l.lower() for l in [
    'Wallpaper',
    'Rosetta Stone'
]]

def send_email_update(new_top_stories):
    if not ADMIN_EMAIL:
        return
    for probe_name in [p for p in new_top_stories][:10]:
        title = new_top_stories[probe_name]['title']
        link = new_top_stories[probe_name]['link']
        # msg = '%s: %s <a href = "%s">%s</a>' % (probe_name, title, link, link)
        msg = '%s: %s' % (title, link)
        if len(new_top_stories) > 10:
            msg += "\n Alert! There are more than 10 top stories in this update"
        subject = "spaceprobes update for %s" % probe_name
        send_email(subject, msg, ADMIN_EMAIL)


def get_search_terms_by_probe():
    # collect search terms from google doc
    search_terms_csv_url = 'https://docs.google.com/spreadsheet/pub?key=0AtHxCskz4p33dEs5elE0eUxfd3Z4VnlXTVliVWJxRHc&single=true&gid=4&output=csv'
    response = requests.get(search_terms_csv_url)
    assert response.status_code == 200, 'Wrong status code'

    search_terms = {}
    for line in response.content.split("\n")[1:]:
        probe_name = line.strip(',').split(',')[0].replace(',',' ').strip()
        search_terms[probe_name.lower()] = [l.strip('"').strip() for l in line.split(',')[1:] if l]  # removes empty strngs

    # sort it alphabetically by probe name
    search_terms_sorted = OrderedDict()
    for probe_name in sorted(search_terms, key=lambda key: search_terms[key]):
        search_terms_sorted[probe_name] = search_terms[probe_name]

    return search_terms_sorted

def update_topstories():
    """ fetches topstories from rss feeds and updates redis """

    try:
        topstories = loads(r_server.get('topstories'))
    except TypeError:
        topstories = {}

    try:
        topstories_archive = loads(r_server.get('topstories_archive'))
    except TypeError:
        topstories_archive = {}

    search_terms = get_search_terms_by_probe()

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

                    if post.title.find(term) > -1 and max([post.title.lower().find(t) for t in exclude_terms]) < 0:
                        # term is found in post title and title contains no exclude_terms

                        # use feedparser's published_parsed to find the published date as time.struct_time
                        # convert it to a string and that's what gets stored in redis
                        # and convert it to a datetime.datetime object for comparing to other post dates
                        try:
                            published_str = datetime.datetime(*post.published_parsed[:6]).isoformat()
                            published = dateutil.parser.parse(published_str)
                        except AttributeError, e:
                            print e
                            print url
                            print post
                            continue

                        if probe_name in topstories:

                            if post.link.strip() == topstories[probe_name]['link'].strip():
                                continue  # we are already serving this link

                            if published != max([published, dateutil.parser.parse(topstories[probe_name]['published'])]):
                                continue  # the link we already have is the latest, move along

                        # add this story to topstories
                        try:
                            topstories_archive[probe_name] = topstories[probe_name]  # first arvhive the old
                        except KeyError:
                            pass  # there was no archive, nbd this is a newly added probe

                        try:
                            topstories[probe_name] = {'title':post.title, 'link':post.link, 'published': published_str }
                            new_top_stories[probe_name] = topstories[probe_name]

                        except AttributeError:
                            if __name__ != "__main__":
                                print "can't find a post.title, post.link, here is post:"
                                print post
                                continue

    r_server.set('topstories', dumps(topstories))
    r_server.set('topstories_archive', dumps(topstories_archive))

    if new_top_stories:
        # send an email digest!
        print "New Stories Added!"
        print new_top_stories
        send_email_update(new_top_stories)
    else:
        print "no new stories added"

    return topstories

if __name__ == "__main__":
    topstories = update_topstories()
    print 'ok'
