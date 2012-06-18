from urllib import urlencode
import httplib2
import json
import hmac
import hashlib


config = {
    "apikey": "0448ec365f8589121da335e075911ec8406f7d41",
    "secret": "b1641edb368b10998209dae45f6e79eb416178cd",
}

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

def calc_siganture(api_name, secret, content): 
    return hmac.new(secret, api_name+content, hashlib.sha256).hexdigest()

body_content = json.dumps(fingerprint)
args = {"k": config["apikey"], "s": calc_siganture("api/commit-fingerprint", config["secret"], body_content) }

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/commit-fingerprint?%s" % urlencode(args), 
    "POST", body=body_content, 
    headers={'content-type':'application/json'} )
        
print "resp", resp
print "content", content    
    