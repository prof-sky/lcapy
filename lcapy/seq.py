from .sequence import Sequence
from .nexpr import n

def seq(s):

    if s.startswith('{'):
        if not s.endswith('}'):
            raise ValueError('Mismatched braces for %s' % s)
    
    parts = s.split(',')
    N = len(parts)

    vals = []
    m0 = None
    for m, item in enumerate(parts):
        if item.startswith('_'):
            if m0 is not None:
                raise ValueError('Cannot have multiple zero index indicators')
            m0 = m
            item = item[1:]
        try:
            val = int(item)
        except ValueError:
            try:
                val = float(item)
            except ValueError:
                val = complex(item)
        vals.append(val)

    if m0 is None:
        m0 = 0
        
    nv = list(range(-m0, N - m0))
    return Sequence(vals, nv, var=n)
