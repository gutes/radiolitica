from urllib import urlencode
import httplib2
import json
import os
import sys

# fix path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath(__file__) ), "..") )

import security
test_keypair = "0448ec365f8589121da335e075911ec8406f7d41", "b1641edb368b10998209dae45f6e79eb416178cd"

fingerprint = {
    "stationid": "a00001",
    "airtime": 1336351306,
    "fingerprints": [
         { "provider": "echonest",           
           "title":"la garola",
           "artist":"garompatex",
           "more":{
               "songid":"SOOLVGG1366802D39F",
           }},
      ]
 }

body_content = json.dumps(fingerprint)
args = security.sign("/api/add-fingerprint", test_keypair, content = body_content)

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/add-fingerprint?%s" % urlencode(args), 
    "POST", body=body_content, 
    headers={'content-type':'application/json'} )
        
print "resp", resp
print "content", content    
    