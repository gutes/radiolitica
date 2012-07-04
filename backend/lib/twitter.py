import json
import re
from datetime import datetime

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from lib import security
from models import twitter
import logging

class TwitterException(Exception): pass
class TwitterSearchResults(object):
    MENTION_EXPR = re.compile("(@\w+)", re.I)  
    HASHTAG_EXPR = re.compile("(#\w+)", re.I)
    def __init__(self, content):
        self.content = json.loads(content)

    @property
    def refresh_url(self):
        return self.content.get("refresh_url", None)
        
    def tweets(self):
        tweets = self.content.get("results", None)
        if tweets != None:
            return  [twitter.Tweet(tweet_id = tweet["id"],
                     from_id = tweet["from_user_id"],
                     to_id = tweet["to_user_id"] or 0,
                     from_user = tweet["from_user"],
                     to_user = tweet["to_user"] or "",
                     hashtags = TwitterSearchResults.HASHTAG_EXPR.findall(tweet["text"]),
                     mentions = TwitterSearchResults.MENTION_EXPR.findall(tweet["text"]),                                    
                     timestamp = datetime.strptime( tweet["created_at"], "%a, %d %b %Y %H:%M:%S +0000"),
                     text = tweet["text"]) for tweet in tweets]
        return []
                                                                  
    def queue_next_page(self, stream, **kargs):
        next_page = self.content.get("next_page", None)                        
        if next_page: # queue next result page to fetch            
            params = security.sign(kargs["task"],
                                   kargs["keystore"], 
                                   params={"su": next_page, "p": stream.key.urlsafe(), "update_stream":0} )            
            taskqueue.add(url=kargs["task"], params=params, method="GET", queue_name = kargs["queue"]  )
            return True
        return False

class Twitter(object):    
    
    SEARCH_URL = "http://search.twitter.com/search.json%s"
    AVAILABLE_TRENDS = "https://api.twitter.com/1/trends/available.json"
    TRENDS = "https://api.twitter.com/1/trends/%s.json"
    
    def search(self, qs):
        result = urlfetch.fetch(url=Twitter.SEARCH_URL % qs, method=urlfetch.GET)
        if result.status_code == 200:
            return TwitterSearchResults(result.content)
        else:
            raise TwitterException("Twitter.search: invalid status_code:%d" % result.status_code)
    
    
    def availableTrends(self, **filters):
        result = urlfetch.fetch(url=Twitter.AVAILABLE_TRENDS, method=urlfetch.GET)
        if result.status_code == 200:
            results = json.loads(result.content)
            for result in results:
                if all( [(result.get(field, None) == value) for field, value in filters.items()] ):
                    yield result                    
        else:
            raise TwitterException("Twitter.availableTrends: invalid status_code:%d" % result.status_code)
            
    def trends(self, woeid = 1):
        result = urlfetch.fetch(url=Twitter.TRENDS % woeid, method=urlfetch.GET)
        if result.status_code == 200:
            results = json.loads(result.content)
            for result in results:
                trends = result.get("trends", None)
                if trends:
                    for trend in trends:
                        yield trend
                else:
                    raise TwitterException("Twitter.trends: invalid reponse")                
        else:
            raise TwitterException("Twitter.trends: invalid status_code:%d" % result.status_code)

        
        
        
        
        
        
        
        
        
        