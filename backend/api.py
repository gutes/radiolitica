import webapp2
from apis.tweetstream import StatTweetstreamsHandler, AddTweetStreamHandler
from apis.fingerprint import AddFingerprintApiHandler, StatFingerprintsHandler

debug = True

routing_table = [ 
    # tweetstreams API
    webapp2.Route('/api/add-tweetstream', handler = AddTweetStreamHandler, methods=['POST'], name = "add-tweetstream"),
    webapp2.Route('/api/stat-tweetstreams', handler = StatTweetstreamsHandler, methods=['GET'], name = "stat-tweetstreams"),

    # acoustic fingerprint API
    webapp2.Route('/api/add-fingerprint', handler = AddFingerprintApiHandler, methods=['POST'], name = "add-fingerprint"),
    webapp2.Route('/api/stat-fingerprints', handler = StatFingerprintsHandler, methods=['GET'], name = "stat-fingerprints"),    
]

app = webapp2.WSGIApplication(routes = routing_table, config = {}, debug = debug)