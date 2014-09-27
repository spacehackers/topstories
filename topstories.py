import feedparser
import requests
from datetime import datetime
from dateutil import parser

def fetch_news():
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

    news = {}
    for url in news_feeds:
        feed = feedparser.parse(url)
        for post in feed.entries:

            # nowsearch each term against this post.title
            for probe_name, terms in search_terms.items():
                for term in terms:
                    if post.title.find(term) > -1:
                        if probe_name in news:
                            # only replace it if this date is more recent
                            if post.published_parsed == max([post.published_parsed, news[probe_name]['published_parsed']]):
                                news[probe_name] = {'title':post.title, 'link':post.link, 'published_parsed': post.published_parsed}

                        else:
                            # add it for first time
                            try:
                                news[probe_name] = {'title':post.title, 'link':post.link, 'published_parsed': post.published_parsed}
                            except AttributeError:
                                if __name__ != "__main__":
                                    print "can't find a post.title, post.link, or post.published, next is post:"
                                    print post

    return news

if __name__ == "__main__":
    import json
    news = fetch_news()
    for n, p in news.items():
        print "%s:" % n
        print p
        print '==='
