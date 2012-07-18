import webapp2
from webapp2_extras import routes
import json
from uuid import uuid4
import logging

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from lib import security
import keystore

class PublishPoint(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.handlers = []
    def add_handler(self, uri, handler, methods):
        self.handlers.append( (uri, handler, methods) )
        
    def routes(self):
        return routes.PathPrefixRoute(self.prefix,[webapp2.Route(name, handler = handler, methods=methods)
                                                   for name, handler, methods in self.handlers])
    def fullpath(self, partial_uri):
        if not partial_uri.startswith("/"):
            partial_uri = "/" + partial_uri
        return self.prefix + partial_uri

class DefaultArgMapper(object):
    def __init__(self, _handler, **kargs):            
        self.has_body = kargs.get("body", False)
        self.has_handler = kargs.get("handler", False)
        self.arg_names, self.arg_defaults = self._map_args(_handler)
                
    def _map_args(self, request_handler):         
        # python black magic to get the name of the function parameters
        handler_expected_args = request_handler.func_code.co_varnames[:request_handler.func_code.co_argcount]        
        
        if request_handler.func_defaults: 
            handler_default_args = dict( zip(handler_expected_args[-len(request_handler.func_defaults):],request_handler.func_defaults) )
        else:
            handler_default_args = {}        
                              
        if self.has_handler: # if handler is required we have to remove it from the expected parameters list
            handler_expected_args = handler_expected_args[1:]
        if self.has_body: # if body is required we have to remove it from the expected parameters list
            handler_expected_args = handler_expected_args[1:]
            
        return handler_expected_args, handler_default_args
        
    def __call__(self, handler):
        # add context if necesary
        handler_final_args = []
        # check for known parameters            
        for arg_name in self.arg_names:
            items = handler.request.GET.getall(arg_name)
            if len(items) == 0: # not found, so use a default value if any.
                try:
                    handler_final_args.append( self.arg_defaults[arg_name] )
                except KeyError,e:
                    raise InvalidApiParameter()
            elif len(items) == 1: # use the supplied value (WITHOUT any validation)
                handler_final_args.append( items[0] )
            else:
                raise InvalidApiParameter()                                        
        return handler_final_args
    
class  DefaultJSONBodyMapper(object):
    @staticmethod
    def serialize( response ):        
        return {'Content-Type':'application/json'}, json.dumps(response)
                        
    @staticmethod
    def parse( headers, body ):
        if headers['Content-Type'] == 'application/json': # fail if not json.
            try:
                return json.loads(body)
            except Exception,e:
                raise InvalidApiBody()
        raise InvalidApiBody()


class Publisher(object):
    API = PublishPoint("/api")
    TASK = PublishPoint("/private/task")

    @staticmethod
    def routing_table(*roles):
        return [role.routes() for role in roles]        

    @staticmethod
    def _build_request_wrapper(request_handler, **kargs):
        # dynamic class
        class RequestHandler(webapp2.RequestHandler): pass        

        inject_handler = kargs.get("handler", False)
        include_body =  kargs.get("body", False)

        handler_arg_mapper = kargs.get("arg_mapper", DefaultArgMapper(request_handler, **kargs) )
        handler_body_mapper = kargs.get("body_mapper", DefaultJSONBodyMapper )

        RequestHandler.ARG_MAPPER  = handler_arg_mapper
        RequestHandler.BODY_MAPPER = handler_body_mapper

        request_filters = kargs.get("filters", [])
        def _handler(handler):
            # apply request filters
            for request_filter in request_filters:
                if not request_filter(handler):
                    return # if any fail, silently abort the request.
            # argument mapping    
            args = []
            if inject_handler: # if necesary inject the handler as first argument                
                args.append( handler )                                
            if include_body: #include the body as second argument.
                args.append( handler_body_mapper.parse(handler.request.headers, handler.request.body) )
            
            #expand argument (extract from request by default)
            args.extend( handler_arg_mapper(handler) )                

            
            response = request_handler(*args) # exceute handler, 
            if response:                
                headers, content = handler_body_mapper.serialize( response ) # serialize the response.                                     
                handler.response.headers.update(headers) # configure the response headers
                handler.response.write( content ) # write the response as JSON
            
            
        if include_body: #use POST if we request a body for the api.
            RequestHandler.post = _handler
            methods = ("POST",)
        else:
            RequestHandler.get =  _handler            
            methods = ("GET",)
        
        return RequestHandler, methods

    @staticmethod
    def publish(_role, _uri, _handler, **kargs):                
        _handler, methods = Publisher._build_request_wrapper(_handler, **kargs)        
        if not _uri.startswith("/"):
            _uri = "/"+_uri
        _role.add_handler(_uri, _handler, methods)
        _handler.URI = _role.fullpath(_uri)
        _handler.METHODS = methods
        return _handler, methods
    

class InvalidApiParameter(Exception): pass
class InvalidApiBody(Exception): pass


#
# main decorarors
#

# export and API
def api(api_uri, **kargs ):
    
    def _wrap_function( handler ):
        request_filters = []
        if kargs.get("check_signature", True ): # add signature checking by default            
            signature_checker = security.SignatureChecker( kargs.get("keypair", keystore.API_KEYSTORE) )
            request_filters.append( signature_checker.as_filter() )            
        kargs["filters"] = request_filters
        # register this handler as an API
        Publisher.publish(Publisher.API, api_uri, handler, **kargs)
    return _wrap_function


class TaskWrapper(object):
    def __init__(self, task_handler ):
        self.task_handler = task_handler

    def __call__(self, *args, **kargs):         
        # setup parameters
        params = dict( zip(self.task_handler.ARG_MAPPER.arg_names, args) )
        params.update( kargs )

        queue_parameters = {
            "params":params,     
        }    
        body = kargs.get("body", None)        
        if body:
            del params["body"]
            method = "POST"
            headers, content = self.task_handler.BODY_MAPPER.serialize( body )
            queue_parameters["payload"] = content
            queue_parameters["headers"] = headers            
            queue_parameters["method"] = "POST"
        else:
            queue_parameters["method"] = "GET"            
                           
        if self.task_handler.QUEUE:
            queue_parameters["queue_name"] = self.task_handler.QUEUE
                        
        taskqueue.add(url=self.task_handler.URI, **queue_parameters)
        
# export a Task
def task(task_name = None, **kargs ):
    def _wrap_function(task_func_handler):                
        api_uri = task_name or str(uuid4().get_hex()) # pseudo random task name, if it is absent                
                
        max_retry_count = kargs.get("retries", 0)
        def _check_retry_count(handler):
            retry_count = handler.request.headers.get("X-AppEngine-TaskRetryCount", None)
            if retry_count:
                return int(retry_count) <= max_retry_count
            return True
            
        kargs["filters"] = [ _check_retry_count, ]            
        requet_handler, _ = Publisher.publish(Publisher.TASK, api_uri, task_func_handler, **kargs)
        requet_handler.QUEUE = kargs.get("queue", None)

        return TaskWrapper(requet_handler)
        
    return _wrap_function
