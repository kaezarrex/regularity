

def recurse(o, callback, key=None):
    '''Recurse through an arbitrary nesting of dicts and lists, calling the 
       callback at each key.

       This function makes one assumption: everything in a list represents the
       same datatype. Every element in the same list will be passed to the 
       callback with the same key. That is just how this function works.

       For example, if you have the object:

       o = {
           'a' : 1,
           'b' : 2,
           'c' : [3,4,5],
           'd' : {
               'e' : 6
               'f' : [7,8]
           }
       }

       then the callback will be called eight times, with the following parameters

       'a', 1
       'b', 2
       'c', 3
       'c', 4
       'c', 5
       'd.e', 6
       'd.f', 7
       'd.f', 8

       @param o : dict|list
           the object to recurse through
       @param callback : function(key, value) -> newvalue
           the callback function, which accepts a key (str) and a value
           if the function returns something, then that returned value replaces
           value.
       @param key : tuple(str)
           a tuple of the dictionary keys that have been processed to get to 
           this point in the object'''

    if isinstance(o, (list, tuple)):
        _o = list()
        for i in o:
            _o.append(recurse(i, callback, key=key))

        return _o

    elif isinstance(o, dict):
        if key is None:
            key = tuple()

        _o = dict()
        for _key in o:
            _o[_key] = recurse(o[_key], callback, key + (_key,))

        return _o

    else:
        _value = callback('.'.join(key), o)
        if _value is not None:
            return _value
        return o
            
