from good import Schema, Optional, Extra, Reject, Invalid, Any, Fallback, Coerce
from glue import MongoCRUD

league_validator = Schema({
    'steam_id' : Coerce(int),
    'is_tracked' : Coerce(bool)
})

class Leagues(MongoCRUD):
    def __init__(self, db):
        super().__init__(db, 'leagues', league_validator)
