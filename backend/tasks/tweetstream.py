import webapp2
import urllib

from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from models import twitter
import keystore

from lib import security
from lib import utils
from lib.twitter import Twitter, TwitterException
from lib import log

from lib import publish

#@publish.task("cron/update-tweetstreams")
@publish.api("update-tweetstreams")
def cron_update_tweetstreams():
    for tweetstream in twitter.TweetStream.query().fetch():
        log.info("updating tweetstream (station-id:%s qs:%s)." % (tweetstream.station_id,tweetstream.stream_query) )
        # queue a task
        refresh_tweetstream( tweetstream.key.urlsafe() ) #queue a task for every tweetstream to update
        
        
@publish.task("refresh-tweetstream", queue = "fetch-tweets")
def refresh_tweetstream( tweetstream_key ):    
    
    log.info("refreshing tweetstream %s" % tweetstream_key  )
        
    # the stream to update        
    stream = twitter.TweetStream.get_by_urlsafe(tweetstream_key)    

    # refresh the query
    s = Twitter.search( qs = stream.stream_query ) # based on the query string
    s.fetch(process_tweets, {"stream-key":tweetstream_key})

@publish.task("process-tweets", queue = "process-tweets")
def process_tweets(results, context):
    stream = twitter.TweetStream.get_by_urlsafe( context["stream-key"] )    

    log.info("processing tweets station-id:%s" % stream.station_id )
    
    # update the refresh url. (en todos los request, puede cambiar ?)
    stream.stream_query = results["refresh_url"]
    stream.put()
        
    tweets = [ twitter.Tweet.from_dict(tweet) for tweet in results["results"] ]
    if tweets:
        # update Tweets in this timeframe
        twitter.Tweets( stream = stream.key,
                        start = min(tweets, key = lambda x:x.timestamp).timestamp,
                        end = max(tweets, key = lambda x:x.timestamp).timestamp,
                        tweets = tweets ).put()
    
    log.info("fetched tweets (station-id:%s count: %d)" % (stream.station_id, len(tweets)) )
    
