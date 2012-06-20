import webapp2
import json

import model
import security
import keystore

class AddTweetStreamHandler(webapp2.RequestHandler):
    
    @security.check_signature("/api/add-tweetstream", keystore.API_KEYSTORE)    
    def post(self):        
        self.response.headers['Content-Type'] = 'application/json'
        data = json.loads(self.request.body)
        model.TweetStream(station_id = data["station_id"],
                          search_url = data["search_url"]).put()
        
class StatTweetstreamsHandler(webapp2.RequestHandler):
    
    @security.check_signature("/api/stat-tweetstreams", keystore.API_KEYSTORE)
    def get(self):        
        self.response.headers['Content-Type'] = 'application/json'
        
        response = {}
        for tweetstream in model.TweetStream.query().fetch():            
            response[tweetstream.key.urlsafe()] = {"last-update": str(tweetstream.last_update),
                                                   "tweets-count": model.Tweet.query( model.Tweet.stream == tweetstream.key ).count() }
                                                                       
        self.response.out.write( json.dumps(response) )
        
        
                
        
