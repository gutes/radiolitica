from google.appengine.ext import ndb 
#
# Social interactions
#
class TweetStream(ndb.Model):
    station_id = ndb.StringProperty(required = True)
    search_url = ndb.StringProperty()
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

class Tweets(ndb.Model):
    stream = ndb.KeyProperty(kind = TweetStream, required = True)
    start = ndb.DateTimeProperty(required = True)
    end = ndb.DateTimeProperty(required = True)
    tweets = ndb.LocalStructuredProperty(Tweet, repeated = True)
