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
    elif bool(string) == string:
        return bool(string)
    else:
        raise ValueError('Expected boolean value, got ' + str(string))

class Leagues():
    def __init__(self, db):
        self.db = MongoCRUD(db, 'leagues', league_validator)

    def _update_tracking_status(self, steam_id, new_status):
        try:
            league = self.db.read(steam_id=int(steam_id))
            self.db.update(league['_id'], {'is_tracked':new_status})
        except KeyError:
            league = self.db.create(steam_id=int(steam_id), is_tracked=new_status)
        return str(league['_id'])

    def track(self, steam_id):
        return self._update_tracking_status(steam_id, True)

    def untrack(self, steam_id):
        return self._update_tracking_status(steam_id, False)

    def list(self, is_tracked = None):
        if is_tracked == None:
            return self.db.list()
        else:
            return self.db.list(is_tracked=read_bool(is_tracked))

