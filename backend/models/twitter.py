import json
import re
from datetime import datetime
from google.appengine.ext import ndb 
#
# Social interactions
#
class TweetStream(ndb.Model):
    station_id = ndb.StringProperty(required = True)
    stream_query = ndb.StringProperty()
    last_update = ndb.DateTimeProperty( auto_now = True)
    
    @classmethod
    def get_by_urlsafe(klass, k):
        return ndb.Key(urlsafe = k).get()


class Tweet(ndb.Model):
    timestamp = ndb.DateTimeProperty(required = True)
    tweet_id = ndb.IntegerProperty(required = True)
    from_user = ndb.StringProperty(required = True)
    from_id = ndb.IntegerProperty(required = True)    
    to_user = ndb.StringProperty(required = True)    
    to_id = ndb.IntegerProperty(required = True)    
    text = ndb.StringProperty(required = True)
    hashtags = ndb.StringProperty(repeated = True)
    mentions = ndb.StringProperty(repeated = True)
    
    # parse a tweet from a json blob.
    MENTION_EXPR = re.compile("(@\w+)", re.I)  
    HASHTAG_EXPR = re.compile("(#\w+)", re.I)    
    
    @staticmethod
    def from_dict( tweet ):
        return  Tweet(tweet_id = tweet["id"],
                      from_id = tweet["from_user_id"],
                      to_id = tweet["to_user_id"] or 0,
                      from_user = tweet["from_user"],
                      to_user = tweet["to_user"] or "",
                      hashtags = Tweet.HASHTAG_EXPR.findall(tweet["text"]),
                      mentions = Tweet.MENTION_EXPR.findall(tweet["text"]),                                    
                      timestamp = datetime.strptime( tweet["created_at"], "%a, %d %b %Y %H:%M:%S +0000"),
                      text = tweet["text"])
    

class Tweets(ndb.Model):
    stream = ndb.KeyProperty(kind = TweetStream, required = True)
    start = ndb.DateTimeProperty(required = True)
    end = ndb.DateTimeProperty(required = True)
    tweets = ndb.LocalStructuredProperty(Tweet, repeated = True)
