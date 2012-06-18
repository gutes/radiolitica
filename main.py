import webapp2
import json
import hmac
import hashlib


from api import FingerprintApiHandler, SocialApiHandler, ListFingerprintsHandler, ListSocialHandler

config = {}
routing_table = [webapp2.Route('/api/commit-fingerprint', handler = FingerprintApiHandler, methods=['POST'], name = "commit-fingerprint"),
                 webapp2.Route('/api/commit-social', handler = SocialApiHandler, methods=['POST'], name = "commit-social"),
                 webapp2.Route('/api/list-fingerprints', handler = ListFingerprintsHandler, methods=['GET'], name = "list-fingerprints"),
                 webapp2.Route('/api/list-social', handler = ListSocialHandler, methods=['GET'], name = "list-social"),
                 ]
app = webapp2.WSGIApplication(routes = routing_table, config = config, debug = True)