from flask import Flask, make_response, request
from config import parse
from glue import expose_as_api
from leagues import Leagues
import os
from pymongo import MongoClient, version
from json import dumps

config = parse('config.yml')
mongo = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017).dota2league_tracker
app = Flask(__name__)

#TODO: add more depth here
@app.route('/health')
def get_health():
    return "Ok"

@app.route('/config')
def get_config():
    return dumps(config)

leagues = Leagues(mongo)
expose_as_api(app, leagues, '/leagues')

from matches import process_leagues_in_background, process_matches_in_background, Matches

matches = Matches(mongo)
expose_as_api(app, matches, '/matches')


import dota2api
steam_api = dota2api.Initialise(config['steam api key'])

from webhooker import Hooks
hooks = Hooks(config['hooks'])

process_leagues_in_background(leagues, steam_api, matches)
process_matches_in_background(steam_api, matches, hooks)


from glue import p
@app.route('/process_match')
def process_match():
    match_id = request.args.get('match_id')
    #match_id = matches.get_match_to_process()
    p('"Processing" match {} due to direct query'.format(match_id))
    match = steam_api.get_match_details(match_id=match_id)
    hooks.process(match=match)
    matches.mark_as_processed(match_id)
    return 'Done'

if __name__ == "__main__":
    app.run(host='0.0.0.0', **config['server'])
