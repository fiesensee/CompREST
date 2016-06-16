from threading import Timer
from pyelasticsearch import ElasticSearch
from .models import FeedSource
import json, feedparser, pytz, hashlib, base64
import datetime, time

refreshTime = 60*5
timer = None


def restartTimer():
    global timer
    global refreshTime
    try:
        timer.cancel()
        print "timer stopped"
    except:
        pass

    getFeeds()
    timer = Timer(refreshTime, restartTimer)
    timer.start()
    print "timer started"

    return None


def getFeeds():
    print "getting feeds"
    es = ElasticSearch('http://fisensee.ddns.net:9200/')

    query = {"query": {"range": {"date": {"lte": "now-1w/w"}}}}
    oldFeeds = es.search(query, size=300, index='feeds')

    if(len(oldFeeds['hits']['hits']) is not 0):
        es.bulk(es.delete_op(id=feed['_id'], index='feeds',
        doc_type='feed') for feed in oldFeeds['hits']['hits'])


    feedSources = FeedSource.objects.all()
    feeds = []
    defaultText = 'undefined'
    defaultDate = datetime.datetime.now().isoformat()
    utc = pytz.utc
    berlin = pytz.timezone('Europe/Berlin')
    now = datetime.datetime.today()
    dateThreshold = now - datetime.timedelta(weeks=2)

    allUrls = []
    for feedSource in feedSources:
        allUrls.append(feedSource.sourceUrl)

    urls = set(allUrls)
    for url in urls:
        source = feedparser.parse(url)
        for entry in source['items']:
            feed = {
                'title':defaultText,
                'description':defaultText,
                'link':defaultText,
                'date':defaultDate,
                'url': defaultText
            }
            if('title' in entry):
                feed['title'] = entry['title']
            if('description' in entry):
                feed['description'] = entry['description']
            if('link' in entry):
                feed['link'] = entry['link']
            if('published_parsed' in entry):
                date = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                if(date < dateThreshold):
                    break
                utcDate = utc.localize(date)
                feed['date'] = utcDate.astimezone(berlin).isoformat()
            #id creation should be enough for now, but it's made to fail
            if('title' or 'published_parsed' in entry):
                feed['id'] = base64.urlsafe_b64encode(hashlib.sha256((feed['title'] + feed['date']).encode('utf8')).hexdigest())
            else:
                feed['id'] = base64.urlsafe_b64encode(hashlib.sha256((feed['title']).encode('utf8')).hexdigest())
            feed['url'] = url
            feeds.append(feed)



    feedJson = json.dumps(feeds)
    es.bulk((es.index_op(feed) for feed in feeds),
        index = 'feeds',
        doc_type = 'feed')
    print es.refresh('feeds')
