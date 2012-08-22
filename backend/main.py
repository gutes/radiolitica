import webapp2

from lib import publish
from lib.publish import Publisher

from lib.log import setup_logger

setup_logger() # ...

# register tasks
import tasks
import apis
import lib # import helper/worker tasks

import publish_api_test

# WSGI applications    
api = webapp2.WSGIApplication(routes = Publisher.routing_table(Publisher.API), config = {}, debug = True)
private = webapp2.WSGIApplication(routes = Publisher.routing_table(Publisher.TASK), config = {}, debug = True)