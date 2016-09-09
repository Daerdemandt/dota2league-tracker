from flask import Flask, abort, request
from config import parse
from bson.json_util import dumps

config = parse('config.yml')

app = Flask(__name__)

#TODO: add more depth here
@app.route('/health')
def get_health():
    return "Ok"

@app.route('/config')
def get_config():
    return dumps(config)

if __name__ == "__main__":
    app.run(host='0.0.0.0', **config['server'])
