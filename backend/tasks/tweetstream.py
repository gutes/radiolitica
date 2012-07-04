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
            
            
            