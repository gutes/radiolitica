import webapp2
import json
import hmac
import hashlib
import model
from google.appengine.ext import ndb
from webob import exc
from keystore import KEYSTORE
from datetime import datetime

class InvalidSignature(Exception): pass

def check_signature(api_path):        
    def _checker(func):
        def checked(self, *args, **kargs):
            # naive signature checks
            k = self.request.GET.getall('k')
            if len(k) != 1:
                raise InvalidSignature()
            # BUGBUG: timming attack
            secret = KEYSTORE.get(k[0], None)
            if secret == None:
                raise InvalidSignature()            
            s = self.request.GET.getall('s')
            if len(k) != 1:
                raise InvalidSignature()
            expected_signature = hmac.new(secret, api_path+self.request.body, hashlib.sha256).hexdigest()            
            if expected_signature != s[0]:
                raise InvalidSignature()
            return func(self, *args, **kargs)        
        return checked
    return _checker
    

class FingerprintApiHandler(webapp2.RequestHandler):

    @check_signature("api/commit-fingerprint")
    def post(self):                 
        data = json.loads(self.request.body)
        
                
        fingerprints = [ model.FingerprintMatch( provider = f["provider"], 
                                                 title = f["title"],
                                                 artist = f["artist"], 
                                                 more = json.dumps(f["more"]) ) for f in data["fingerprints"] ] 

        fingerprint = model.Fingerprint( station_id = data["stationid"], 
                                         airtime = data["airtime"],
                                         fingerprints = fingerprints)
        fingerprint.put()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request.body)


class SocialApiHandler(webapp2.RequestHandler):

    @check_signature("api/commit-social")
    def post(self):                 
        data = json.loads(self.request.body)        
        if data["provider"] == "twitter":                        
            tweets = [ model.Tweet( tweet_id = tweet["id"],
                                    from_id = tweet["from_id"],
                                    to_id = tweet["to_id"] or 0,
                                    from_user = tweet["_from"],
                                    to_user = tweet["_to"] or "",
                                    hashtags = tweet["hashtags"],
                                    mentions = tweet["mentions"],
                                    timestamp = datetime.strptime( tweet["created_at"], "%Y-%m-%d %H:%M:%S"),
                                    text = tweet["text"]) for tweet in data["events"]]

            tweetstream = model.TweetStream(station_id = data["station_id"],
                                            begin = datetime.strptime( data["begin"], "%Y-%m-%d %H:%M:%S"),
                                            end = datetime.strptime( data["end"], "%Y-%m-%d %H:%M:%S"),
                                            events = tweets)            
            tweetstream.put()            
        else:
            raise Exception("Invalid social provider")

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request.body)




class ListFingerprintsHandler(webapp2.RequestHandler):

    @check_signature("api/list-fingerprints")    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        for fingerprint in model.Fingerprint.query().fetch():
            self.response.out.write( "%s\n" % str(fingerprint) )

class ListSocialHandler(webapp2.RequestHandler):

    @check_signature("api/list-social")    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        for fingerprint in model.TweetStream.query().fetch():
            self.response.out.write( "%s\n" % str(fingerprint) )