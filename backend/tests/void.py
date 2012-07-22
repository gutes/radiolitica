import sys

def unique( func ):        
    print "%s:%s:%s" % ( str(__name__), func.func_code.co_name, func.func_code.co_firstlineno )    
    return func
    
@unique
def some_function():
    pass