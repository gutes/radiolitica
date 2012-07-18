
from models import fingerprint
from lib import publish
import json

@publish.api("add-fingerprint", body = True)
def add_fingerprint(body):
    fingerprints = [ fingerprint.FingerprintMatch( provider = f["provider"], 
                                                   title = f["title"],
                                                   artist = f["artist"], 
                                                   more = json.dumps(f["more"]) ) for f in body["fingerprints"] ] 

    fingerprint.Fingerprint( station_id = body["stationid"],
                             airtime = body["airtime"],
                             fingerprints = fingerprints).put()

@publish.api("stat-fingerprints")
def stat_fingerprints():
    return {
        "count": fingerprint.Fingerprint.query().count()
    }
