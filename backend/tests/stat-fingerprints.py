from urllib import urlencode
import httplib2
import json
import os
import sys

# fix path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath(__file__) ), "..") )

from lib import security
test_keypair = "0448ec365f8589121da335e075911ec8406f7d41", "b1641edb368b10998209dae45f6e79eb416178cd"

args = security.sign("/api/stat-fingerprints", test_keypair)

h = httplib2.Http()
resp, content = h.request("http://127.0.0.1:8081/api/stat-fingerprints?%s" % urlencode(args),"GET")
        
print "resp", resp
print "content", content    
    