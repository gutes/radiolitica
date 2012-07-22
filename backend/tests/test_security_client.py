from urllib import urlencode
import httplib2
import json

import sys
import os
# fix path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath(__file__) ), "..") )

from lib import security
import keystore
    
    
test_keypair = "0448ec365f8589121da335e075911ec8406f7d41", "b1641edb368b10998209dae45f6e79eb416178cd"    


#body = json.dumps( {"body":42, "carlos":23} )
#params = {"a":"test", "b":"manolo", "c": 33, "d":"n+1"}
#
#uri = "/api/testcase-params"
#args = security.sign(uri, test_keypair, params = params, content = body)
#h = httplib2.Http()
#resp, content = h.request("http://127.0.0.1:8081%s?%s" % (uri, urlencode(args)),  
#    "POST", body=body, 
#    headers={'content-type':'application/json'} )
#        
#
#        
#print "resp", resp
#print "content", content    
#
#print "<------>"
#
#uri = "/api/testcase-current"
#params = security.sign(uri, test_keypair)
#h = httplib2.Http()
#resp, content = h.request("http://127.0.0.1:8081%s?%s" % (uri,urlencode(params)), "GET")
#        
#print "resp", resp
#print "content", content    

#
#print "<------>"
#
#uri = "/api/testcase-queuetask"
#params = security.sign(uri, test_keypair )
#resp, content = h.request("http://127.0.0.1:8081%s?%s" % (uri,urlencode(params)), "GET")
#        print "resp", resp
#print "content", content    
#
#
uri = "/api/update-tweetstreams"
params = security.sign(uri, test_keypair )
h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081%s?%s" % (uri,urlencode(params)), "GET")
print "resp", resp
print "content", content    

