from konf import Konf
from good import Schema, Optional, Extra, Reject, Invalid, Any, Fallback
from collections import Counter
from webhooker import template_schema

#TODO: use messages to explain what's wrong in the config
is_valid_server_conf = Schema({
    'port' : Any(int, Fallback(5000)),
    'debug' : Any(bool, Fallback(True))
})

is_valid_hooklist = Schema({
    Extra : template_schema
})

def parse(filename):
    k = Konf(filename)

    # syntax:
    config = {
        'server' : k('server', is_valid_server_conf),
        'steam api key' : k('steam api key', str),
        'hooks' : k('hooks', is_valid_hooklist)
    }

    # semantics:

    return config

