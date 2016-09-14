from good import Schema, Optional, Extra, Reject, Invalid, Any, Fallback, Coerce
from glue import MongoCRUD

league_validator = Schema({
    'steam_id' : Coerce(int),
    'is_tracked' : Coerce(bool)
})

# TODO: use that in coerce
def read_bool(string):
    if string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    else:
        raise ValueError('Expected boolean value, got ' + str(string))

class Leagues():
    def __init__(self, db):
        self.db = MongoCRUD(db, 'leagues', league_validator)
    def track(self, steam_id):
        raise NotImplementedError
    def untrack(self, steam_id):
        raise NotImplementedError
    def list(self, is_tracked = None):
        if is_tracked == None:
            return self.db.list()
        else:
            return self.db.list(is_tracked=read_bool(is_tracked))
        raise NotImplementedError

