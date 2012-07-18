import webapp2
from lib.publish import Publisher

# register tasks
import tasks
import apis


# WSGI applications
api = webapp2.WSGIApplication(routes = Publisher.routing_table(Publisher.API), config = {}, debug = True)
private = webapp2.WSGIApplication(routes = Publisher.routing_table(Publisher.TASK), config = {}, debug = True)