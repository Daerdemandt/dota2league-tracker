from konf import Konf
from good import Schema, Optional, Extra, Reject, Invalid, Any, Fallback
from collections import Counter

#TODO: use messages to explain what's wrong in the config
is_valid_server_conf = Schema({
    'port' : Any(int, Fallback(5000)),
    'debug' : Any(bool, Fallback(True))
})

def parse(filename):
    k = Konf(filename)

    # syntax:
    config = {
        'server' : k('server', is_valid_server_conf),
        'steam api key' : k('steam api key', str)
    }

    # semantics:

    return config

