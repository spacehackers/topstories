import feedparser
import requests

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
            for probe_name, terms in search_terms.items():
                for term in terms:
                    if post.title.find(term) > -1:
                        news.setdefault(probe_name, []).append({'title':post.title, 'link':post.link, 'published': post.published})
    return news
