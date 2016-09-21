from flask import Flask, make_response
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


import dota2api
steam_api = dota2api.Initialise(config['steam api key'])

from webhooker import Hooks
hooks = Hooks(config['hooks'])

process_leagues_in_background(leagues, steam_api, matches)
process_matches_in_background(steam_api, matches, hooks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', **config['server'])
