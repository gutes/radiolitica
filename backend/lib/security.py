import hmac
import hashlib
import logging

class InvalidSignature(Exception): pass


class SignatureChecker(object):
    def __init__(self, keystore):
        self.keystore = keystore
        
    def __call__(self, handler):
        # naive signature checks
        k = handler.request.GET.getall('k')
        if len(k) != 1:
            return False
        # BUGBUG: timming attack
        secret = self.keystore.get(k[0], None)
        if secret == None:
            return False
        signature = handler.request.GET.getall('s')
        if len(k) != 1:
            return False
        signature = signature[0]    
            
        params = dict(handler.request.GET)
        del params["k"] # remove api-key
        del params["s"] # remove signature
            
        params_content = "&".join( [str(param[0])+"="+str(param[1]) for param in sorted(params.items(), key = lambda x:x[0])] )                    

        shared = handler.request.path+":"+params_content+":"+handler.request.body            
        expected_signature = hmac.new(secret, shared, hashlib.sha256).hexdigest()            

        # validate signature and validate path
        if expected_signature == signature:
            return True # the request is accepted.
            
        return False # the request is rejected.

    def as_decorator(self, func):
        def _sig_checker(handler, *args, **kargs):
            if self(handler):
                return func(handler, *args, **kargs)                        
            raise InvalidSignature()
        return _sig_checker
                
    def as_filter( self ):
        def _filter( handler ):
            if not self(handler):
                raise InvalidSignature()
            return True
        return _filter
            
def check_signature(keystore):    
    return lambda func: SignatureChecker(keystore).as_decorator(func)


def sign(api_path, key_pair, **kargs):
    api_k, secret = key_pair    
    content = kargs.get("content", "")
    params = kargs.get("params", {})            
    params_content = "&".join( [str(param[0])+"="+str(param[1]) for param in sorted(params.items(), key = lambda x:x[0])] )        
    signature = hmac.new(secret, api_path+":"+params_content+":"+content, hashlib.sha256).hexdigest()    
    params.update({"k": api_k, "s":signature})
    return params
    
