from urllib import urlencode
import httplib2
import json

import sys
import os
# fix path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath(__file__) ), "..") )

import security
import keystore
    
params = security.sign("private/test/test-signature", keystore.TEST_KEYPAIR, params = {"a":"test", "b":42} )

h = httplib2.Http()    
resp, content = h.request("http://127.0.0.1:8081/private/test/test-signature?%s" % urlencode(params), "GET")
        
print "resp", resp
print "content", content    
