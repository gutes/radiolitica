import os

def in_appengine():
    return os.environ.get("SERVER_SOFTWARE", None) != None
    
    
if in_appengine(): 
    import twitter # register twitter helper tasks
    