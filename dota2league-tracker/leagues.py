from good import Schema, Optional, Extra, Reject, Invalid, Any, Fallback, Coerce
from glue import MongoCRUD

league_validator = Schema({
    'steam_id' : Coerce(int),
    'is_tracked' : Coerce(bool)
})

class Leagues():
    def __init__(self, db):
        self.db = MongoCRUD(db, 'leagues', league_validator)
    def track(self, steam_id):
        raise NotImplementedError
    def untrack(self, steam_id):
        raise NotImplementedError
    def list(self, tracked = None):
        raise NotImplementedError

