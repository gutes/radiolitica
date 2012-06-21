import webapp2
from tasks.tweetstream import UpdateTweetStreamTask, FetchTweetsSearchTask

debug = True

routing_table = [ 
    # tweetstreams TASK
    webapp2.Route('/private/tasks/update-tweetstreams', handler = UpdateTweetStreamTask, methods=['GET'], name = "task-update-tweetstreams"),
    webapp2.Route('/private/tasks/fetch-tweets', handler = FetchTweetsSearchTask, methods=['GET'], name = "task-fetch-tweets"),
]
if debug:
    from tests.test_security_handler import TestSignatureHandler
    routing_table.append( webapp2.Route('/private/tests/test-signature', handler = TestSignatureHandler, methods=['GET'], name = "test-signature") )

app = webapp2.WSGIApplication(routes = routing_table, config = {}, debug = debug)
