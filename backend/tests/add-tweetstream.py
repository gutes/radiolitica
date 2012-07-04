from urllib import urlencode
import httplib2
import json
import sys
import os

# fix path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath(__file__) ), "..") )

from lib import security

test_keypair = "0448ec365f8589121da335e075911ec8406f7d41", "b1641edb368b10998209dae45f6e79eb416178cd"

command = {
    "station_id": "a0001",
    "search_url": "?q=@la100fm",
}
body_content = json.dumps(command)

args = security.sign("/api/add-tweetstream", test_keypair, content = body_content)

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/add-tweetstream?%s" % urlencode(args), 
    "POST", body=body_content, 
    headers={'content-type':'application/json'} )
        
print "resp", resp
print "content", content    
    