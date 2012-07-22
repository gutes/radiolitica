import logging
                       
def setup_logger():
    import webapp2
    import publish
    
    logger = logging.getLogger("radiolitica")
    class CustomLogFilter(logging.Filter):
        def filter(self, record):
            record.msg = "[%s]: %s" % (publish.request_tag() or "<?>", record.msg)
            return True            
    logger.addFilter( CustomLogFilter() )
    
info = logging.getLogger("radiolitica").info
warning = logging.getLogger("radiolitica").warning
error = logging.getLogger("radiolitica").error
debug = logging.getLogger("radiolitica").debug


        

    