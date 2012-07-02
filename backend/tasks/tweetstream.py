import webapp2
import urllib
import logging
import re
import json
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

import model
import security
import keystore

class CantFetchTweetsException(Exception): pass
class InvalidTweeterResponse(Exception): pass            
class UpdateTweetStreamTask(webapp2.RequestHandler):    
    def get(self):
        for tweetstream in model.TweetStream.query().fetch():
            logging.info("updating tweetstream: " + tweetstream.search_url)            
            
            params = security.sign("/private/tasks/fetch-tweets", 
                                   keystore.TASK_KEYPAIR, 
                                   params={"su": tweetstream.search_url, "p": tweetstream.key.urlsafe() } )

            taskqueue.add(url="/private/tasks/fetch-tweets", params=params, method="GET", queue_name = "fetch-tweets")
                                                                    
mention_expr = re.compile("(@\w+)", re.I)  
hashtag_expr = re.compile("(#\w+)", re.I)
class FetchTweetsSearchTask(webapp2.RequestHandler):

    @security.check_signature("/private/tasks/fetch-tweets", keystore.TASK_KEYSTORE)
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        _k = self.request.GET.getall('su')
        if len(_k) != 1 and len(_k[0]) < 1:
            raise Exception("mmm...invalid request")
        search_url = _k[0]        

        _k = self.request.GET.getall('p')
        if len(_k) != 1 and len(_k[0]) < 1:
            raise Exception("mmm...invalid request")
        parent_entity = _k[0]
        
        result = urlfetch.fetch(url="http://search.twitter.com/search.json%s" % search_url, method=urlfetch.GET)
        if result.status_code == 200:
            search_result = json.loads(result.content)
            
            stream = model.TweetStream.get_by_urlsafe(parent_entity)
            stream.search_url = search_result["refresh_url"]
            stream.put()
                                    
            next_page = search_result.get("next_page", None)                        
            if next_page: # queue next result page to fetch
                params = security.sign("/private/tasks/fetch-tweets",
                                       keystore.TASK_KEYPAIR, 
                                       params={"su": next_page, "p": stream.key.urlsafe() } )            
                taskqueue.add(url="/private/tasks/fetch-tweets", params=params, method="GET", queue_name = "fetch-tweets" )
            tweets = search_result.get("results", None)
            if tweets != None:
                t = [model.Tweet(tweet_id = tweet["id"],
                                 from_id = tweet["from_user_id"],
                                 to_id = tweet["to_user_id"] or 0,
                                 from_user = tweet["from_user"],
                                 to_user = tweet["to_user"] or "",
                                 hashtags = hashtag_expr.findall(tweet["text"]),
                                 mentions = mention_expr.findall(tweet["text"]),                                    
                                 timestamp = datetime.strptime( tweet["created_at"], "%a, %d %b %Y %H:%M:%S +0000"),
                                 text = tweet["text"] ) for tweet in tweets]
                if len(t) > 0:       
                    model.Tweets( stream = stream.key   ,
                                  start = min(t, key = lambda x:x.timestamp).timestamp,
                                  end = max(t, key = lambda x:x.timestamp).timestamp,
                                  tweets = t ).put()
                                  
                logging.info("%s - fetched tweets: %d" % (search_url, len(t)) )
            else:
                raise InvalidTweeterResponse()            
        else:
            raise CantFetchTweetsException()