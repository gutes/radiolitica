import webapp2
import security
import keystore

class TestSignatureHandler(webapp2.RequestHandler):

    @security.check_signature("private/test/test-signature", keystore.TEST_KEYSTORE)
    def get(self):
        # ok.
        pass
