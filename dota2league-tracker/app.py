from flask import Flask
from config import parse
from glue import expose_as_api
from leagues import Leagues
import os
from pymongo import MongoClient, version

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

expose_as_api(app, Leagues(mongo), '/leagues')

@app.route('/obj/')
def get():
    args = request.args
    key = args.get('key')
    #return str([_ for _ in args])
    #args = dict(request.args)
    args = {_:args.get(_) for _ in args}
    return str(args)
    return str(args[key])

if __name__ == "__main__":
    app.run(host='0.0.0.0', **config['server'])
