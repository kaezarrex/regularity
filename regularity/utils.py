

def recurse(o, callback, key=None):
    '''Recurse through an arbitrary nesting of dicts and lists, calling the 
       callback at each key.

       This function makes one assumption: everything in a list represents the
       same datatype. Every element in the same list will be passed to the 
       callback with the same key. That is just how this function works.

       @param o : dict|list
           the object to recurse through
       @param callback : function(key, value) -> newvalue
           the callback function, which accepts a key (str) and a value
           if the function returns something, then that returned value replaces
           value.
       @param key : tuple(str)
           a tuple of the dictionary keys that have been processed to get to 
           this point in the object'''

    if isinstance(o, list):
        for i in xrange(len(o)):
            _value = recurse(o[i], callback, key=key)

            if _value is not None:
                o[i] = _value

    elif isinstance(o, dict):
        if key is None:
            key = tuple()

        for _key in o:
            _value = recurse(o[_key], callback, key + (_key,))

            if _value is not None:
                o[_key] = _value


    else:
        _value = callback('.'.join(key), o)
        return _value
            
        


