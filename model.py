from google.appengine.ext import ndb

#
# Audio fingerprinting
#
class FingerprintMatch(ndb.Model):
    provider = ndb.StringProperty(required = True)
    title = ndb.StringProperty(required = True)
    artist = ndb.StringProperty(required = True)
    # more data about this fingerprint (ie. songid for echonest)
    more = ndb.JsonProperty()        
        
class Fingerprint(ndb.Model):
  station_id = ndb.StringProperty(required = True)
  airtime = ndb.IntegerProperty(required = True)
  fingerprints = ndb.StructuredProperty(FingerprintMatch, repeated=True)
  
 
#
# Social interactions
#
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

class TweetStream(ndb.Model):
    station_id = ndb.StringProperty(required = True)
    begin = ndb.DateTimeProperty(required = True)
    end = ndb.DateTimeProperty(required = True)
    events = ndb.LocalStructuredProperty(Tweet, repeated=True)