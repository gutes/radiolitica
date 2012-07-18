import webapp2
import urllib
import logging
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from models import twitter
import keystore

from lib import security
from lib import utils
from lib.twitter import Twitter, TwitterException



class Test_TwitterApiTask(webapp2.RequestHandler):
    def get(self):
        api = Twitter()
        api.search("@la100fm", 
                   callback = "/private/tasks/process-tweets",  
                   queue = "twitter-processor",
                   keystore = keystore.TASK_KEYPAIR)




class ProcessTweetsTask(webapp2.RequestHandler):
    @security.check_signature("/private/tasks/process-tweets", keystore.TASK_KEYSTORE)    
    def post(self):
        pass


# handle search pages
class TwitterApiFetchResultsTask(webapp2.RequestHandler):

    @security.check_signature("/private/tasks/twitter/fetch-search-results", keystore.TWITTER_API_KEYSTORE)
    def post(self):
        #...
        keypair = security.symmetric_decrypt(keystore.TWITTER_API_KEYPAIR, keypair)
    
        query = "?q=@la100fm"
        queue_name = "twitter-processor"
        callback_url = "/private/tasks/process-tweets"
        keypair = keystore.TASK_KEYPAIR
        state = {}
        
        api = Twitter()        
        result = api.fetch_search(query) # retrieve this resultset from twitter

        # queue next result page, if any.
        result.queue_next_page(
            query = query
            queue_name = queue_name
            callback_url = callback_url
            keypair = keypair
            state = state            
        ) 
        
        # queue results
        tweets = result.tweets()
        if len(tweets):                        
            body = json.dump({"query": query,                              
                              "page": result.page,
                              "tweets": tweets,
                              "start": min(tweets, key = lambda x:x["timestamp"])["timestamp"],
                              "end": max(tweets, key = lambda x:x["timestamp"])["timestamp"],
                              "state":state})                              
            taskqueue.add(url=callback_url+"?"+security.sign(callback_url, keypair, content = body), 
                          payload=body,
                          method="POST",
                          queue_name = queue_name)
    
                
                                


class UpdateTweetStreamTask(webapp2.RequestHandler):    
    def get(self):
        for tweetstream in twitter.TweetStream.query().fetch():
            logging.info("updating tweetstream (station-id:%s qs:%s)." % (tweetstream.station_id,tweetstream.search_url) )                        
            params = security.sign("/private/tasks/fetch-tweets", 
                                   keystore.TASK_KEYPAIR, 
                                   params={"su": tweetstream.search_url, "p": tweetstream.key.urlsafe(), "update_stream":1 } )
            taskqueue.add(url="/private/tasks/fetch-tweets", params=params, method="GET", queue_name = "fetch-tweets")
                                                                    
class FetchTweetsSearchTask(webapp2.RequestHandler):

    @security.check_signature("/private/tasks/fetch-tweets", keystore.TASK_KEYSTORE)
    def get(self):
        # decode GET parameters
        search_url, tweetstream_key, update_stream = utils.parameters(self.request.GET, "su", "p", ("update_stream",lambda x: x==1) )
                        
        twitter_api = Twitter()
        try:
            results = twitter_api.search( search_url )            

            stream = twitter.TweetStream.get_by_urlsafe(tweetstream_key)
            if update_stream: # update refresh url for the next update.        
                stream.search_url = results.refresh_url or stream.search_url
                stream.put()
                                    
            # queue the next page to process.
            results.queue_next_page(stream, 
                                    task = "/private/tasks/fetch-tweets",
                                    queue = "fetch-tweets",
                                    keystore = keystore.TASK_KEYPAIR)                                    
            # process actual tweets
            tweets = results.tweets()
            if tweets:
                # update Tweets in this timeframe
                twitter.Tweets( stream = stream.key,
                                start = min(tweets, key = lambda x:x.timestamp).timestamp,
                                end = max(tweets, key = lambda x:x.timestamp).timestamp,
                                tweets = tweets ).put()            
                                
            logging.info("fetched tweets (station-id:%s qs:%s count: %d)" % (stream.station_id, search_url, len(tweets)) )
            
                                
        except TwitterException,e:
            logging.error( str(e) )        
            
            
            