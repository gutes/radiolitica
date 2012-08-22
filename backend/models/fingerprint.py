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