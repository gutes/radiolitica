import os
from urllib import urlencode
import httplib2
import json
import hmac
import hashlib
from datetime import datetime


config = {
    "apikey": "0448ec365f8589121da335e075911ec8406f7d41",
    "secret": "b1641edb368b10998209dae45f6e79eb416178cd",
}

social = {
    "station_id": "a00001",
    "provider": "twitter",
    "begin": None, 
    "end": None,
    "events": None,        
 }

# in case we're not running inside /test directory
test_tweets_path = os.path.join(os.path.abspath( __file__ )[:os.path.abspath( __file__ ).rfind("/")], "tweets.json")

with open(test_tweets_path) as f:
    social["events"] = json.loads(f.read())

def calculate_timespan_for_tweetstream(tweets):
    timeline = [datetime.strptime( tweet["created_at"], "%Y-%m-%d %H:%M:%S") for tweet in tweets]
    return str(min(timeline)), str(max(timeline))

begin, end = calculate_timespan_for_tweetstream(social["events"])    
social["begin"] = begin
social["end"] = end
    
def calc_siganture(api_name, secret, content): 
    return hmac.new(secret, api_name+content, hashlib.sha256).hexdigest()

body_content = json.dumps(social)
args = {"k": config["apikey"], "s": calc_siganture("api/commit-social", config["secret"], body_content) }

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/commit-social?%s" % urlencode(args), 
    "POST", body=body_content, 
    headers={'content-type':'application/json'} )
        
print "resp", resp
print "content", content    
    