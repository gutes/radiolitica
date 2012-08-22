import types

class InvalidParameterInRequest(Exception): pass
def parameters(param_container, *params ):
    ret = []
    for param in params:        
        items = []         
        if type(param) == types.TupleType:
            items.append( param )
        elif type(param) in types.StringTypes:
            items.append( (param, None) )                    
        for item in items:
            _k = param_container.getall( item[0] )
            if len(_k) != 1 and len(_k[0]) < 1:
                raise InvalidParameterInRequest("%s" % param)
            ret.append( (item[1] and item[1](_k[0]) ) or _k[0] )            
    return tuple(ret)

            


    
    
    
    
    