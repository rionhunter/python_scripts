import feedparser

def get_rss_feed(url, limit=5):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary
        })
    return articles