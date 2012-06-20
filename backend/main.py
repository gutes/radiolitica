import webapp2
from api.tweetstream import StatTweetstreamsHandler, AddTweetStreamHandler
from api.fingerprint import AddFingerprintApiHandler, StatFingerprintsHandler

from tasks.tweetstream import UpdateTweetStreamTask, FetchTweetsSearchTask

debug = True

routing_table = [ 
    # tweetstreams API
    webapp2.Route('/api/add-tweetstream', handler = AddTweetStreamHandler, methods=['POST'], name = "add-tweetstream"),
    webapp2.Route('/api/stat-tweetstreams', handler = StatTweetstreamsHandler, methods=['GET'], name = "stat-tweetstreams"),

    # tweetstreams TASK
    webapp2.Route('/private/task/update-tweetstreams', handler = UpdateTweetStreamTask, methods=['GET'], name = "task-update-tweetstreams"),
    webapp2.Route('/private/task/fetch-tweets', handler = FetchTweetsSearchTask, methods=['GET'], name = "task-fetch-tweets"),
    
    # acoustic fingerprint API
    webapp2.Route('/api/add-fingerprint', handler = AddFingerprintApiHandler, methods=['POST'], name = "add-fingerprint"),
    webapp2.Route('/api/stat-fingerprints', handler = StatFingerprintsHandler, methods=['GET'], name = "stat-fingerprints"),    
]

if debug:
    from tests.test_security_handler import TestSignatureHandler
    routing_table.append( webapp2.Route('/private/test/test-signature', handler = TestSignatureHandler, methods=['GET'], name = "test-signature") )

app = webapp2.WSGIApplication(routes = routing_table, config = {}, debug = debug)
