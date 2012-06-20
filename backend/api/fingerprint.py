import webapp2
import json

import security
import model
import keystore

class AddFingerprintApiHandler(webapp2.RequestHandler):

    @security.check_signature("/api/add-fingerprint", keystore.API_KEYSTORE)
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

class StatFingerprintsHandler(webapp2.RequestHandler):

    @security.check_signature("/api/stat-fingerprints", keystore.API_KEYSTORE)    
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        
        response = {
            "count": model.Fingerprint.query().count()
        }
        self.response.out.write( json.dumps(response) )
            
        
