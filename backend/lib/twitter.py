import json
from datetime import datetime
from urllib import urlencode
import urlparse

from google.appengine.api import urlfetch

from models import twitter
from lib import publish
from lib import log

class TwitterException(Exception): pass

@publish.task("twitter-search-page-worker", queue = "fetch-tweets")
def twitter_search_page_worker(callback_blob, query_string, context):
    
    # fetch with retry.    
    max_retry = 3
    retry = max_retry        
    while retry:
        try:
            response = urlfetch.fetch(url=TwitterSearchRequest.URL % query_string, method=urlfetch.GET)
            break # request complete
        except Exception, e:            
            retry -= 1 # another try.
            retry_in = (2 ** (max_retry-retry)) * 1000
            log.warning("Twitter.twitter_search_page_worker: urlfetch retry #%d (sleep %ds)" % (max_retry-retry, retry_in) )
            time.sleep( retry_in )
                        
    if response.status_code == 200:
        results = json.loads(response.content) # decode json response
        retry = 0 # request finished
    else:
        raise TwitterException("Twitter.task.twitter_search_page_worker: invalid status_code: %d" % result.status_code)
    
    # deserialize the callback task.
    callback = publish.Task( urlsafe = callback_blob )
    callback(results, context)
            
    # queue next page if any
    next_page_query_string = results.get("next_page", None)                     
    if next_page_query_string:
        twitter_search_page_worker(callback_blob, next_page_query_string, context) # queue next page

class TwitterSearchRequest(object):
    URL = "http://search.twitter.com/search.json%s"
        
    def __init__(self, query, **kargs):
        self.query = query
        self.args = kargs

    @staticmethod
    def fromQS(qs):
        try:
            params = dict( urlparse.parse_qsl(urlparse.urlparse(qs).query) ) # WARNING: merge duplicates.
            q = params["q"]
            del params["q"] # remove q from parameters
            return TwitterSearchRequest(q, **params)
        except Exception,e:
            raise TwitterException("TwitterSearchRequest.fromQS:"+str(e) )
        
    def fetch(self, callback, context = None):
        # queue task to fetch
        twitter_search_page_worker(callback.urlsafe(), self.query_string(), context or {} )
            
    def query_string(self):        
        qs = {"q":self.query}
        qs.update(self.args)        
        return "?" + urlencode(qs)

    def __str__(self):
        return self.query_string()
    
class Twitter(object):
    AVAILABLE_TRENDS = "https://api.twitter.com/1/trends/available.json"
    TRENDS = "https://api.twitter.com/1/trends/%s.json"
            
    @staticmethod
    def search(query = None, **kargs):        
        qs = kargs.get("qs", None)
        if qs:
            return TwitterSearchRequest.fromQS(qs)            
        if query == None:
            raise TwitterException("Twitter.search: invalid query string.")
        return TwitterSearchRequest(query, **kargs)        

    
    def availableTrends(self, **filters):
        result = urlfetch.fetch(url=Twitter.AVAILABLE_TRENDS, method=urlfetch.GET)
        if result.status_code == 200:
            results = json.loads(result.content)
            for result in results:
                if all( [(result.get(field, None) == value) for field, value in filters.items()] ):
                    yield result                    
        else:
            raise TwitterException("Twitter.availableTrends: invalid status_code:%d" % result.status_code)
            
    def trends(self, woeid = 1): # 1 = worldwide
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

        
        
        
        
        
        
        
        
        
        