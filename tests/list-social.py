from urllib import urlencode
import httplib2
import json
import hmac
import hashlib


config = {
    "apikey": "0448ec365f8589121da335e075911ec8406f7d41",
    "secret": "b1641edb368b10998209dae45f6e79eb416178cd",
}

def calc_siganture(api_name, secret, content = ""): 
    return hmac.new(secret, api_name+content, hashlib.sha256).hexdigest()

args = {"k": config["apikey"], "s": calc_siganture("api/list-social", config["secret"]) }

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/list-social?%s" % urlencode(args),"GET")
        
print "resp", resp
print "content", content    
    