import hmac
import hashlib
import logging

class InvalidSignature(Exception): pass
def check_signature(api_path, keystore):        
    def _checker(func):
        def checked(self, *args, **kargs):
            # naive signature checks
            k = self.request.GET.getall('k')
            if len(k) != 1:
                raise InvalidSignature()
            # BUGBUG: timming attack
            secret = keystore.get(k[0], None)
            if secret == None:
                raise InvalidSignature()            
            signature = self.request.GET.getall('s')
            if len(k) != 1:
                raise InvalidSignature()
            signature = signature[0]    
            
            params = dict(self.request.GET)
            del params["k"] # remove api-key
            del params["s"] # remove signature
            
            params_content = "&".join( [str(param[0])+"="+str(param[1]) for param in sorted(params.items(), key = lambda x:x[0])] )                    

            shared = self.request.path+":"+params_content+":"+self.request.body            
            expected_signature = hmac.new(secret, shared, hashlib.sha256).hexdigest()            

            if expected_signature != signature:
                raise InvalidSignature()
                
            # validate path
            if api_path != self.request.path:
                raise InvalidSignature()
            
            return func(self, *args, **kargs)        
        return checked
    return _checker


def sign(api_path, key_pair, **kargs):
    api_k, secret = key_pair    
    content = kargs.get("content", "")
    params = kargs.get("params", {})            
    params_content = "&".join( [str(param[0])+"="+str(param[1]) for param in sorted(params.items(), key = lambda x:x[0])] )        
    signature = hmac.new(secret, api_path+":"+params_content+":"+content, hashlib.sha256).hexdigest()    
    params.update({"k": api_k, "s":signature})
    return params
    
