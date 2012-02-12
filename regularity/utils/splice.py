from itertools import chain
from operator import itemgetter

def splice(dots=None, dashes=None, pendings=None, reverse=False):
    '''Splice together the dots, dashes and pendings for chronological listing.
       This function injects a 'type' key into each object, as the return value
       is just a single list. The 'type' key will be either 'dot', 'dash', or
       'pending'.
      
       @param dots : optional, list|tuple(dict)
           the dots to splice in
       @param dashes : optional, list|tuple(dict)
           the dashes to splice in
       @param pendings : optional, list|tuple(dict)
           the pendings to splice in'''

    if dots is None:
        dots = list()

    if dashes is None:
        dashes = list()

    if pendings is None:
        pendings = list()

    for dot in dots:
        dot['type'] = 'dot'
        dot['key'] = dot['time']

    for dash in dashes:
        dash['type'] = 'dash'
        dash['key'] = dash['end']

    for pending in pendings:
        pending['type'] = 'pending'
        pending['key'] = pending['start']

    return sorted(chain(dots, dashes, pendings), key=itemgetter('key'), reverse=reverse)

