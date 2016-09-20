import time
import threading
from glue import p, forever

class Matches:
    def __init__(self, db):
        self._db = db['match_statuses']
        self._new = set()
        self._processed = set()

    def list(self, status):
        if status == 'new':
            return list(self._new)
        elif status == 'processed':
            return list(self._processed)
        else:
            raise ValueError('Requested matches with status {}. Supported statuses are `new` and `processed`')

    def counts(self):
        return {
            'new' : len(self._new),
            'processed' : len(self._processed)
        }

    def add(self, match_id):
        if match_id in self._processed:
            return
        else:
            self._new.add(match_id)
        
    def get_match_to_process(self):
        return self._new.pop()

    def mark_as_processed(self, match_id): # TODO use mongoqueue to remove race conditions
        self._processed.add(match_id)
        if match_id in self._new:
            self._new.remove(match_id)

def process_leagues_in_background(leagues, dota_api, matches):
    p('Process leagues started!')
    def process_league(league_id):
        new_matches = dota_api.get_match_history(laegue_id=league_id)['matches']
        for match in new_matches:
            matches.add(match['match_id'])

    def process_leagues():
        tracked = [l['_id'] for l in leagues.list(is_tracked='true')] # TODO: figure out why True does not work
        for league_id in tracked:
            process_league(league_id)

    forever(process_leagues, 3000)# TODO: read delay from config

def process_matches_in_background(dota_api, matches):
    p('Process matches started!')
    def process_one():
        match_id = matches.get_match_to_process()
        p('"Processing" match {}'.format(match_id))
        matches.mark_as_processed(match_id)
    forever(process_one, 2)
